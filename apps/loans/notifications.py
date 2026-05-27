import logging

from django.conf import settings
from django.core.mail import send_mail

from apps.transactions.services import get_user_wallet

from .models import Loan, LoanApplication

logger = logging.getLogger(__name__)

SUPPORT_EMAIL = getattr(
    settings,
    "SUPPORT_EMAIL",
    getattr(settings, "DEFAULT_FROM_EMAIL", "support@pennycreditonline.com"),
)

APPLICATION_NOTIFY_STATUSES = frozenset(
    {
        LoanApplication.Status.PENDING,
        LoanApplication.Status.APPROVED,
        LoanApplication.Status.REJECTED,
        LoanApplication.Status.CANCELLED,
    }
)

LOAN_NOTIFY_STATUSES = frozenset(
    {
        Loan.Status.APPROVED,
        Loan.Status.REJECTED,
        Loan.Status.CLOSED,
    }
)

APPLICATION_STATUS_SUBJECTS = {
    LoanApplication.Status.PENDING: "Loan application received",
    LoanApplication.Status.APPROVED: "Loan application approved",
    LoanApplication.Status.REJECTED: "Loan application rejected",
    LoanApplication.Status.CANCELLED: "Loan application cancelled",
}

LOAN_STATUS_SUBJECTS = {
    Loan.Status.APPROVED: "Loan approved",
    Loan.Status.REJECTED: "Loan rejected",
    Loan.Status.CLOSED: "Loan closed",
}

APPLICATION_STATUS_INTROS = {
    LoanApplication.Status.PENDING: (
        "Thank you for applying with PennyCredit. We have received your loan application "
        "and it is now pending review. No funds have been debited from your wallet. "
        "You will receive another email when a decision has been made."
    ),
    LoanApplication.Status.APPROVED: (
        "We are pleased to inform you that your loan application has been approved. "
        "Your loan has been set up and the approved amount has been credited to your wallet."
    ),
    LoanApplication.Status.REJECTED: (
        "We regret to inform you that your loan application was not approved at this time. "
        "No funds were debited from your wallet for this application."
    ),
    LoanApplication.Status.CANCELLED: (
        "Your loan application has been cancelled. "
        "No funds were debited from your wallet for this application."
    ),
}

LOAN_STATUS_INTROS = {
    Loan.Status.APPROVED: (
        "Your loan has been approved. The loan amount has been credited to your wallet "
        "and your repayment schedule is active."
    ),
    Loan.Status.REJECTED: (
        "Your loan has been marked as rejected. No additional disbursement was made "
        "to your wallet for this loan."
    ),
    Loan.Status.CLOSED: (
        "Your loan has been closed. Please review the summary below and contact support "
        "if you have any questions about your account."
    ),
}


def _format_money(amount, currency_code: str = "USD") -> str:
    return f"{amount:,.2f} {currency_code}"


def _status_change_line(old_status: str | None, new_status: str, *, model_cls) -> str:
    if not old_status:
        return f"Status: {model_cls(new_status).label}"
    old_label = model_cls(old_status).label
    new_label = model_cls(new_status).label
    return f"Status: {old_label} → {new_label}"


def _disbursement_lines(disbursement_info: dict | None) -> list[str]:
    if not disbursement_info:
        return []
    lines = [
        "",
        "DISBURSEMENT",
        "────────────────────────────────────────",
        f"Amount credited: {_format_money(disbursement_info['amount'], disbursement_info['currency_code'])}",
        f"Loan reference: {disbursement_info['loan_reference']}",
    ]
    if disbursement_info.get("monthly_payment") is not None:
        lines.append(
            f"Estimated monthly repayment: "
            f"{_format_money(disbursement_info['monthly_payment'], disbursement_info['currency_code'])}"
        )
    if disbursement_info.get("interest_rate") is not None:
        lines.append(f"Interest rate: {disbursement_info['interest_rate']}% per annum")
    if disbursement_info.get("term_months"):
        lines.append(f"Loan term: {disbursement_info['term_months']} months")
    if disbursement_info.get("outstanding_balance") is not None:
        lines.append(
            f"Outstanding balance: "
            f"{_format_money(disbursement_info['outstanding_balance'], disbursement_info['currency_code'])}"
        )
    if disbursement_info.get("wallet_balance") is not None:
        lines.append(
            f"Current wallet balance: "
            f"{_format_money(disbursement_info['wallet_balance'], disbursement_info['currency_code'])}"
        )
    if disbursement_info.get("disbursed_on"):
        lines.append(f"Disbursed on: {disbursement_info['disbursed_on']:%A, %d %B %Y}")
    return lines


def _support_section(reference_code: str) -> list[str]:
    return [
        "",
        "NEED ASSISTANCE?",
        "────────────────────────────────────────",
        "Our support team is here to help with any questions about your loan.",
        f"Email: {SUPPORT_EMAIL}",
        f"Reference to quote: {reference_code}",
        "Please include your registered email address and the reference code above when you contact us.",
    ]


def _build_application_email_body(
    application: LoanApplication,
    *,
    old_status: str | None,
    disbursement_info: dict | None = None,
) -> str:
    user = application.user
    greeting_name = user.first_name or user.display_name
    intro = APPLICATION_STATUS_INTROS.get(
        application.status, "Your loan application has been updated."
    )

    lines = [
        f"Dear {greeting_name},",
        "",
        intro,
        "",
        "LOAN APPLICATION SUMMARY",
        "────────────────────────────────────────",
        f"Application reference: {application.reference_code}",
        _status_change_line(old_status, application.status, model_cls=LoanApplication.Status),
        f"Product: {application.product.name}",
        f"Requested amount: {_format_money(application.requested_amount)}",
        f"Term: {application.term_months} months",
        f"Purpose: {application.purpose}",
        f"Submitted: {application.created_at:%A, %d %B %Y at %H:%M UTC}",
        f"Last updated: {application.updated_at:%A, %d %B %Y at %H:%M UTC}",
    ]
    lines.extend(_disbursement_lines(disbursement_info))
    lines.extend(
        [
            "",
            "ACCOUNT",
            "────────────────────────────────────────",
            f"Name: {user.full_name or user.display_name}",
            f"Email: {user.email}",
        ]
    )
    lines.extend(_support_section(application.reference_code))
    lines.extend(
        [
            "",
            "WHAT YOU SHOULD DO",
            "────────────────────────────────────────",
            "1. Sign in to your PennyCredit dashboard to view your loan and wallet balance.",
            "2. Review your repayment schedule and upcoming due dates.",
            "3. Contact support if you need any assistance.",
            "4. Keep this email for your records.",
            "",
            "— PennyCredit",
            "This is an automated notification. Please do not reply to this email.",
        ]
    )
    return "\n".join(lines)


def _build_loan_email_body(
    loan: Loan,
    *,
    old_status: str | None,
    disbursement_info: dict | None = None,
) -> str:
    user = loan.user
    greeting_name = user.first_name or user.display_name
    intro = LOAN_STATUS_INTROS.get(loan.status, "Your loan status has been updated.")

    lines = [
        f"Dear {greeting_name},",
        "",
        intro,
        "",
        "LOAN SUMMARY",
        "────────────────────────────────────────",
        f"Loan reference: {loan.reference_code}",
        _status_change_line(old_status, loan.status, model_cls=Loan.Status),
        f"Product: {loan.product.name}",
        f"Principal amount: {_format_money(loan.principal_amount)}",
        f"Interest rate: {loan.interest_rate}% per annum",
        f"Term: {loan.term_months} months",
        f"Outstanding balance: {_format_money(loan.outstanding_balance)}",
        f"Applied on: {loan.applied_on:%A, %d %B %Y}",
        f"Last updated: {loan.updated_at:%A, %d %B %Y at %H:%M UTC}",
    ]
    if loan.application_id:
        lines.append(f"Application reference: {loan.application.reference_code}")
    lines.extend(_disbursement_lines(disbursement_info))
    wallet = get_user_wallet(user)
    if wallet and not disbursement_info:
        lines.extend(
            [
                "",
                "WALLET",
                "────────────────────────────────────────",
                f"Current available balance: {_format_money(wallet.balance, wallet.currency_code)}",
            ]
        )
    lines.extend(
        [
            "",
            "ACCOUNT",
            "────────────────────────────────────────",
            f"Name: {user.full_name or user.display_name}",
            f"Email: {user.email}",
        ]
    )
    lines.extend(_support_section(loan.reference_code))
    lines.extend(
        [
            "",
            "WHAT YOU SHOULD DO",
            "────────────────────────────────────────",
            "1. Sign in to your PennyCredit dashboard to review your loan details.",
            "2. Keep this email for your records.",
            "3. Contact support if you need any assistance.",
            "",
            "— PennyCredit",
            "This is an automated notification. Please do not reply to this email.",
        ]
    )
    return "\n".join(lines)


def send_loan_application_status_email(
    application: LoanApplication,
    *,
    old_status: str | None,
    disbursement_info: dict | None = None,
) -> None:
    if application.status not in APPLICATION_NOTIFY_STATUSES:
        return
    if old_status == application.status:
        return

    user = application.user
    if not user.email:
        return

    status_prefix = APPLICATION_STATUS_SUBJECTS.get(
        application.status, "Loan application update"
    )
    subject = f"PennyCredit — {status_prefix} ({application.reference_code})"
    message = _build_application_email_body(
        application, old_status=old_status, disbursement_info=disbursement_info
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@pennycreditonline.com"),
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send loan application email for %s to %s",
            application.reference_code,
            user.email,
        )


def send_loan_status_email(
    loan: Loan,
    *,
    old_status: str | None,
    disbursement_info: dict | None = None,
) -> None:
    if loan.status not in LOAN_NOTIFY_STATUSES:
        return
    if old_status == loan.status:
        return

    user = loan.user
    if not user.email:
        return

    status_prefix = LOAN_STATUS_SUBJECTS.get(loan.status, "Loan update")
    subject = f"PennyCredit — {status_prefix} ({loan.reference_code})"
    message = _build_loan_email_body(
        loan, old_status=old_status, disbursement_info=disbursement_info
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@pennycreditonline.com"),
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send loan status email for %s to %s",
            loan.reference_code,
            user.email,
        )
