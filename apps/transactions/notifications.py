import logging
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail

from apps.transactions.services import DEBIT_CATEGORIES, WALLET_CATEGORIES, get_user_wallet

from .models import Transaction

SUPPORT_EMAIL = getattr(
    settings,
    "SUPPORT_EMAIL",
    getattr(settings, "DEFAULT_FROM_EMAIL", "support@pennycreditonline.com"),
)
logger = logging.getLogger(__name__)

NOTIFY_STATUSES = frozenset(
    {
        Transaction.Status.PENDING,
        Transaction.Status.COMPLETED,
        Transaction.Status.FAILED,
        Transaction.Status.REFUNDED,
        Transaction.Status.REJECTED,
        Transaction.Status.CANCELLED,
    }
)

STATUS_SUBJECTS = {
    Transaction.Status.PENDING: "Transaction received",
    Transaction.Status.COMPLETED: "Transaction completed",
    Transaction.Status.FAILED: "Transaction failed",
    Transaction.Status.REFUNDED: "Transaction refunded",
    Transaction.Status.REJECTED: "Transaction rejected",
    Transaction.Status.CANCELLED: "Transaction cancelled",
}

STATUS_INTROS = {
    Transaction.Status.PENDING: (
        "Thank you for using PennyCredit. We have received your transaction and it is "
        "currently pending review. The details are confirmed below. You will receive "
        "another email when the status changes."
    ),
    Transaction.Status.COMPLETED: (
        "Your transaction has been processed successfully. "
        "The details below reflect the final state of this transaction."
    ),
    Transaction.Status.FAILED: (
        "We regret to inform you that your transaction could not be completed and has "
        "been marked as failed. Any funds that were reserved or debited for this "
        "transaction have been returned to your wallet where applicable. "
        "Please review the details below and contact our support team if you need "
        "assistance or have questions about this transaction."
    ),
    Transaction.Status.REFUNDED: (
        "Your transaction has been refunded. "
        "Any debited funds for this transfer or withdrawal have been returned to your wallet. "
        "Please contact our support team if you have any questions."
    ),
    Transaction.Status.REJECTED: (
        "Your transaction was reviewed and could not be processed. "
        "Any debited funds for this transfer or withdrawal have been returned to your wallet. "
        "Please contact our support team if you need assistance."
    ),
    Transaction.Status.CANCELLED: (
        "Your transaction has been cancelled. "
        "If funds were debited for a transfer or withdrawal, they have been returned to your wallet "
        "where applicable. Contact support if you have any questions."
    ),
}

REFUND_NOTIFY_STATUSES = frozenset(
    {
        Transaction.Status.FAILED,
        Transaction.Status.REJECTED,
        Transaction.Status.REFUNDED,
        Transaction.Status.CANCELLED,
    }
)

def _format_money(amount: Decimal, currency_code: str) -> str:
    return f"{amount:,.2f} {currency_code}"


def _status_change_line(old_status: str | None, new_status: str) -> str:
    if not old_status:
        return f"Status: {Transaction.Status(new_status).label}"
    old_label = Transaction.Status(old_status).label
    new_label = Transaction.Status(new_status).label
    return f"Status: {old_label} → {new_label}"


def _pending_wallet_lines(transaction: Transaction) -> list[str]:
    if transaction.status != Transaction.Status.PENDING:
        return []
    amount = _format_money(transaction.amount, transaction.currency_code)
    if transaction.category in DEBIT_CATEGORIES:
        return [
            f"Amount reserved: −{amount} has been debited from your wallet pending processing.",
            "Funds will remain reserved until this transaction is completed or resolved.",
        ]
    if transaction.category == Transaction.Category.DEPOSIT:
        lines = ["Your deposit is awaiting verification by our team."]
        if transaction.crypto_symbol and transaction.crypto_amount:
            lines.append(
                f"Crypto submitted: {transaction.crypto_amount:,.8f} {transaction.crypto_symbol}"
            )
        lines.append("Your wallet will be credited once the deposit is approved.")
        return lines
    return []


def _wallet_impact_line(transaction: Transaction) -> str | None:
    if transaction.status != Transaction.Status.COMPLETED:
        return None
    if transaction.category not in WALLET_CATEGORIES:
        return None
    amount = _format_money(transaction.amount, transaction.currency_code)
    if transaction.category == Transaction.Category.DEPOSIT:
        return f"Wallet impact: +{amount} credited to your account"
    if transaction.category == Transaction.Category.WITHDRAWAL:
        return f"Wallet impact: −{amount} debited from your account"
    return f"Wallet impact: −{amount} debited for this transfer"


def _refund_lines(refund_info: dict | None) -> list[str]:
    if not refund_info:
        return []
    amount = _format_money(refund_info["amount"], refund_info["currency_code"])
    return [
        f"Refund applied: {amount} has been credited back to your wallet.",
        "Your available balance has been updated accordingly.",
    ]


def _crypto_wallet_line(transaction: Transaction, wallet) -> str | None:
    if not transaction.crypto_symbol or not transaction.crypto_amount:
        return None
    field_map = {
        "BTC": "btc_balance",
        "ETH": "eth_balance",
        "USDT": "usdt_balance",
        "SOL": "sol_balance",
    }
    field = field_map.get((transaction.crypto_symbol or "").upper())
    if not field or not wallet:
        return None
    balance = getattr(wallet, field)
    return (
        f"{transaction.crypto_symbol} wallet balance: "
        f"{balance:,.8f} {transaction.crypto_symbol}"
    )


def _build_detail_lines(
    transaction: Transaction,
    *,
    old_status: str | None,
    refund_info: dict | None = None,
) -> list[str]:
    user = transaction.user
    lines = [
        "TRANSACTION SUMMARY",
        "────────────────────────────────────────",
        f"Reference: {transaction.reference_code}",
        _status_change_line(old_status, transaction.status),
        f"Category: {transaction.get_category_display()}",
        f"Direction: {transaction.get_direction_display()}",
        f"Fiat amount: {_format_money(transaction.amount, transaction.currency_code)}",
    ]

    if transaction.crypto_symbol and transaction.crypto_amount:
        lines.append(
            f"Crypto amount: {transaction.crypto_amount:,.8f} {transaction.crypto_symbol}"
        )

    if transaction.description:
        lines.append(f"Description: {transaction.description}")

    if transaction.counterparty_name:
        lines.append(f"Counterparty: {transaction.counterparty_name}")

    if transaction.transaction_hash:
        lines.append(f"Transaction hash: {transaction.transaction_hash}")

    lines.extend(
        [
            f"Transaction ID: {transaction.id}",
            f"Created: {transaction.created_at:%A, %d %B %Y at %H:%M UTC}",
            f"Last updated: {transaction.updated_at:%A, %d %B %Y at %H:%M UTC}",
        ]
    )

    wallet = get_user_wallet(user, transaction.currency_code)
    wallet_section: list[str] = []
    wallet_section.extend(_pending_wallet_lines(transaction))
    if transaction.status in REFUND_NOTIFY_STATUSES:
        wallet_section.extend(_refund_lines(refund_info))
        if (
            not refund_info
            and transaction.category in DEBIT_CATEGORIES
        ):
            wallet_section.append(
                "No wallet refund was applied — this transaction had not debited your wallet."
            )
    wallet_impact = _wallet_impact_line(transaction)
    if wallet_impact:
        wallet_section.append(wallet_impact)
    if wallet:
        wallet_section.append(
            f"Current available balance: {_format_money(wallet.balance, wallet.currency_code)}"
        )
        crypto_line = _crypto_wallet_line(transaction, wallet)
        if crypto_line:
            wallet_section.append(crypto_line)
    if wallet_section:
        lines.extend(["", "WALLET", "────────────────────────────────────────", *wallet_section])

    lines.extend(
        [
            "",
            "ACCOUNT",
            "────────────────────────────────────────",
            f"Name: {user.full_name or user.display_name}",
            f"Email: {user.email}",
        ]
    )
    return lines


def _build_support_section(reference_code: str) -> list[str]:
    return [
        "",
        "NEED ASSISTANCE?",
        "────────────────────────────────────────",
        "Our support team is here to help with any questions about this transaction.",
        f"Email: {SUPPORT_EMAIL}",
        f"Reference to quote: {reference_code}",
        "Please include your registered email address and the reference code above when you contact us.",
    ]


def _build_next_steps(transaction: Transaction) -> list[str]:
    if transaction.status == Transaction.Status.PENDING:
        return [
            "",
            "WHAT HAPPENS NEXT",
            "────────────────────────────────────────",
            "1. Our team will review your transaction.",
            "2. You will receive another email when the status is updated.",
            "3. Sign in to your PennyCredit dashboard to track progress at any time.",
            "4. Contact support if you need assistance or did not initiate this transaction.",
        ]
    if transaction.status in REFUND_NOTIFY_STATUSES:
        return [
            "",
            "WHAT YOU SHOULD DO",
            "────────────────────────────────────────",
            "1. Review the transaction summary and wallet section above.",
            "2. Sign in to your PennyCredit dashboard to confirm your current balance.",
            "3. Contact support if you need assistance or did not initiate this transaction.",
            "4. Keep this email for your records.",
        ]
    return [
        "",
        "NEXT STEPS",
        "────────────────────────────────────────",
        "1. Sign in to your PennyCredit dashboard to view your transaction history and balances.",
        "2. Keep this email for your records.",
        "3. Contact support if you need assistance or did not authorize this transaction.",
    ]


def _build_email_body(
    transaction: Transaction,
    *,
    old_status: str | None,
    refund_info: dict | None = None,
) -> str:
    user = transaction.user
    greeting_name = user.first_name or user.display_name
    intro = STATUS_INTROS.get(transaction.status, "Your transaction has been updated.")

    body_lines = [
        f"Dear {greeting_name},",
        "",
        intro,
        "",
    ]
    body_lines.extend(
        _build_detail_lines(transaction, old_status=old_status, refund_info=refund_info)
    )
    body_lines.extend(_build_support_section(transaction.reference_code))
    body_lines.extend(_build_next_steps(transaction))
    body_lines.extend(
        [
            "",
            "— PennyCredit",
            "This is an automated notification. Please do not reply to this email.",
        ]
    )
    return "\n".join(body_lines)


def send_transaction_status_email(
    transaction: Transaction,
    *,
    old_status: str | None,
    refund_info: dict | None = None,
) -> None:
    if transaction.status not in NOTIFY_STATUSES:
        return
    if old_status == transaction.status:
        return

    user = transaction.user
    if not user.email:
        return

    category_label = transaction.get_category_display()
    status_prefix = STATUS_SUBJECTS.get(transaction.status, "Transaction update")
    subject = (
        f"PennyCredit — {status_prefix}: {category_label} "
        f"({transaction.reference_code})"
    )
    message = _build_email_body(
        transaction, old_status=old_status, refund_info=refund_info
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
