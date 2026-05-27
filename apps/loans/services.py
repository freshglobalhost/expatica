from datetime import date
from decimal import Decimal

from django.db import transaction

from apps.core.utils import generate_reference_code
from apps.wallets.models import Wallet

from .models import Loan, LoanApplication, LoanRepayment


def _add_months(start: date, months: int) -> date:
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    days_in_month = [
        31,
        29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ][month - 1]
    day = min(start.day, days_in_month)
    return date(year, month, day)


def _monthly_payment(principal: Decimal, annual_rate: Decimal, term_months: int) -> Decimal:
    if term_months <= 0:
        return principal
    if annual_rate <= 0:
        return (principal / term_months).quantize(Decimal("0.01"))
    monthly_rate = annual_rate / Decimal("100") / 12
    factor = (1 + monthly_rate) ** term_months
    payment = principal * monthly_rate * factor / (factor - 1)
    return payment.quantize(Decimal("0.01"))


def get_user_wallet(user, currency_code: str = "USD") -> Wallet | None:
    return (
        Wallet.objects.filter(user=user, currency_code=currency_code).first()
        or Wallet.objects.filter(user=user).order_by("currency_code").first()
    )


def build_disbursement_info(loan: Loan, wallet: Wallet | None) -> dict:
    first_repayment = loan.repayments.order_by("due_on").first()
    monthly_payment = first_repayment.amount if first_repayment else None
    currency_code = wallet.currency_code if wallet else "USD"
    return {
        "amount": loan.principal_amount,
        "currency_code": currency_code,
        "loan_reference": loan.reference_code,
        "wallet_balance": wallet.balance if wallet else None,
        "interest_rate": loan.interest_rate,
        "term_months": loan.term_months,
        "monthly_payment": monthly_payment,
        "outstanding_balance": loan.outstanding_balance,
        "disbursed_on": loan.disbursed_on,
    }


@transaction.atomic
def disburse_loan_principal(loan: Loan) -> dict | None:
    """Credit loan principal to the user's wallet when a loan is approved."""
    wallet = get_user_wallet(loan.user)
    if not wallet:
        return None

    if loan.disbursed_on:
        return build_disbursement_info(loan, wallet)

    wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
    wallet.balance += loan.principal_amount
    wallet.save(update_fields=["balance", "updated_at"])

    today = date.today()
    loan.disbursed_on = today
    if loan.status in (Loan.Status.PENDING, Loan.Status.APPROVED):
        loan.status = Loan.Status.ACTIVE
    loan.save(update_fields=["disbursed_on", "status", "updated_at"])

    return build_disbursement_info(loan, wallet)


@transaction.atomic
def create_loan_from_approved_application(
    application: LoanApplication,
) -> tuple[Loan | None, dict | None]:
    """Create an active loan, repayment schedule, and disburse funds to the wallet."""
    if application.status != LoanApplication.Status.APPROVED:
        return None, None
    if hasattr(application, "loan") and application.loan_id:
        loan = application.loan
        wallet = get_user_wallet(application.user)
        return loan, build_disbursement_info(loan, wallet)

    product = application.product
    principal = application.requested_amount
    term_months = application.term_months
    interest_rate = product.minimum_interest_rate
    today = date.today()
    payment = _monthly_payment(principal, interest_rate, term_months)

    loan = Loan.objects.create(
        user=application.user,
        application=application,
        product=product,
        reference_code=generate_reference_code("LN"),
        principal_amount=principal,
        interest_rate=interest_rate,
        term_months=term_months,
        status=Loan.Status.ACTIVE,
        applied_on=today,
        disbursed_on=today,
        outstanding_balance=principal,
    )

    due_start = today
    for month_offset in range(1, term_months + 1):
        LoanRepayment.objects.create(
            loan=loan,
            amount=payment,
            due_on=_add_months(due_start, month_offset),
        )

    wallet = get_user_wallet(application.user)
    if wallet:
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        wallet.balance += principal
        wallet.save(update_fields=["balance", "updated_at"])

    return loan, build_disbursement_info(loan, wallet)
