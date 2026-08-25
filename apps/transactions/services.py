from decimal import Decimal

from django.db import transaction as db_transaction

from apps.wallets.models import Wallet

from .models import Transaction

WALLET_CATEGORIES = frozenset(
    {
        Transaction.Category.DEPOSIT,
        Transaction.Category.WITHDRAWAL,
        Transaction.Category.TRANSFER,
    }
)

DEBIT_CATEGORIES = frozenset(
    {
        Transaction.Category.WITHDRAWAL,
        Transaction.Category.TRANSFER,
    }
)

REFUND_STATUSES = frozenset(
    {
        Transaction.Status.FAILED,
        Transaction.Status.REJECTED,
        Transaction.Status.REFUNDED,
        Transaction.Status.CANCELLED,
    }
)

TERMINAL_REFUND_STATUSES = REFUND_STATUSES


def get_user_wallet(user, currency_code: str) -> Wallet | None:
    return (
        Wallet.objects.filter(user=user, currency_code=currency_code).first()
        or Wallet.objects.filter(user=user).order_by("currency_code").first()
    )


def prepare_admin_transaction(obj: Transaction) -> str | None:
    """
    For deposit / withdrawal / transfer created in admin: set direction and status,
    and credit or debit the user's wallet. Returns an error message, or None on success.
    """
    if obj.category not in WALLET_CATEGORIES:
        return None

    if obj.category == Transaction.Category.DEPOSIT:
        obj.direction = Transaction.Direction.CREDIT
    else:
        obj.direction = Transaction.Direction.DEBIT

    wallet = get_user_wallet(obj.user, obj.currency_code)
    if not wallet:
        return "No wallet found for this user."

    with db_transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

        if obj.category in (Transaction.Category.WITHDRAWAL, Transaction.Category.TRANSFER):
            if obj.amount <= Decimal("0"):
                return "Amount must be greater than zero."
            if wallet.balance < obj.amount:
                return (
                    f"Insufficient wallet balance "
                    f"({wallet.balance} {wallet.currency_code})."
                )
            wallet.balance -= obj.amount
            wallet.save(update_fields=["balance", "updated_at"])
        elif obj.amount > Decimal("0"):
            wallet.balance += obj.amount
            wallet.save(update_fields=["balance", "updated_at"])

        obj.status = Transaction.Status.COMPLETED

    return None


def apply_transfer_withdrawal_refund(
    transaction: Transaction,
    old_status: str | None,
) -> dict | None:
    """
    Transfer and withdrawal are pending by default with the wallet debited upfront.
    If admin marks failed, rejected, or refunded, credit the amount back to the wallet.
    """
    if transaction.category not in DEBIT_CATEGORIES:
        return None
    if transaction.status not in REFUND_STATUSES:
        return None
    if old_status in TERMINAL_REFUND_STATUSES:
        return None
    if old_status not in (Transaction.Status.PENDING, Transaction.Status.COMPLETED):
        return None

    is_crypto = bool(transaction.crypto_symbol and transaction.crypto_amount)
    if not is_crypto and transaction.amount <= Decimal("0"):
        return None

    wallet = get_user_wallet(transaction.user, transaction.currency_code)
    if not wallet:
        return None

    with db_transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        if is_crypto:
            field = wallet.crypto_balance_field(transaction.crypto_symbol)
            if not field:
                return None
            current = getattr(wallet, field)
            setattr(wallet, field, current + transaction.crypto_amount)
            wallet.save(update_fields=[field, "updated_at"])
            return {
                "action": "refunded_to_crypto_wallet",
                "amount": transaction.crypto_amount,
                "currency_code": transaction.crypto_symbol,
                "is_crypto": True,
            }

        wallet.balance += transaction.amount
        wallet.save(update_fields=["balance", "updated_at"])

    return {
        "action": "refunded_to_wallet",
        "amount": transaction.amount,
        "currency_code": wallet.currency_code,
    }