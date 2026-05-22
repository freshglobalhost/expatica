import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import Transaction

logger = logging.getLogger(__name__)

NOTIFY_STATUSES = frozenset(
    {
        Transaction.Status.COMPLETED,
        Transaction.Status.FAILED,
        Transaction.Status.REFUNDED,
        Transaction.Status.REJECTED,
    }
)

STATUS_SUBJECTS = {
    Transaction.Status.COMPLETED: "Transaction completed",
    Transaction.Status.FAILED: "Transaction failed",
    Transaction.Status.REFUNDED: "Transaction refunded",
    Transaction.Status.REJECTED: "Transaction rejected",
}


def send_transaction_status_email(transaction: Transaction, *, old_status: str | None) -> None:
    if transaction.status not in NOTIFY_STATUSES:
        return
    if old_status == transaction.status:
        return

    user = transaction.user
    if not user.email:
        return

    status_label = transaction.get_status_display()
    subject_prefix = STATUS_SUBJECTS.get(transaction.status, "Transaction update")
    subject = f"PennyCredit — {subject_prefix}"

    amount_line = f"{transaction.amount} {transaction.currency_code}"
    if transaction.crypto_symbol and transaction.crypto_amount:
        amount_line = f"{transaction.crypto_amount} {transaction.crypto_symbol} ({amount_line})"

    message = (
        f"Hello {user.first_name or user.display_name},\n\n"
        f"Your transaction {transaction.reference_code} is now: {status_label}.\n\n"
        f"Description: {transaction.description or transaction.get_category_display()}\n"
        f"Amount: {amount_line}\n"
        f"Category: {transaction.get_category_display()}\n"
        f"Date: {transaction.created_at:%Y-%m-%d %H:%M UTC}\n\n"
        "Sign in to your dashboard for full details.\n\n"
        "— PennyCredit"
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
            "Failed to send transaction status email for %s to %s",
            transaction.reference_code,
            user.email,
        )
