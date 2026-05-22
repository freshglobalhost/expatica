import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import LoanApplication

logger = logging.getLogger(__name__)

SUPPORT_EMAIL = getattr(
    settings,
    "SUPPORT_EMAIL",
    getattr(settings, "DEFAULT_FROM_EMAIL", "support@pennycreditonline.com"),
)

NOTIFY_STATUSES = frozenset(
    {
        LoanApplication.Status.PENDING,
        LoanApplication.Status.APPROVED,
        LoanApplication.Status.REJECTED,
        LoanApplication.Status.CANCELLED,
    }
)

STATUS_SUBJECTS = {
    LoanApplication.Status.PENDING: "Loan application received",
    LoanApplication.Status.APPROVED: "Loan application approved",
    LoanApplication.Status.REJECTED: "Loan application rejected",
    LoanApplication.Status.CANCELLED: "Loan application cancelled",
}

STATUS_INTROS = {
    LoanApplication.Status.PENDING: (
        "Thank you for applying with PennyCredit. We have received your loan application "
        "and it is now pending review. No funds have been debited from your wallet. "
        "You will receive another email when a decision has been made."
    ),
    LoanApplication.Status.APPROVED: (
        "We are pleased to inform you that your loan application has been approved. "
        "Your loan will be set up according to the terms below and funds will be "
        "disbursed to your wallet. No upfront debit was taken from your account for "
        "this application."
    ),
    LoanApplication.Status.REJECTED: (
        "We regret to inform you that your loan application was not approved at this time. "
        "No funds were debited from your wallet for this application. "
        "Please review the details below and contact support if you have questions."
    ),
    LoanApplication.Status.CANCELLED: (
        "Your loan application has been cancelled. "
        "No funds were debited from your wallet for this application. "
        "Contact support if you did not request this cancellation or need assistance."
    ),
}


def _format_money(amount, currency_code: str = "USD") -> str:
    return f"{amount:,.2f} {currency_code}"


def _build_email_body(application: LoanApplication, *, old_status: str | None) -> str:
    user = application.user
    greeting_name = user.first_name or user.display_name
    intro = STATUS_INTROS.get(application.status, "Your loan application has been updated.")
    product_name = application.product.name

    lines = [
        f"Dear {greeting_name},",
        "",
        intro,
        "",
        "LOAN APPLICATION SUMMARY",
        "────────────────────────────────────────",
        f"Reference: {application.reference_code}",
    ]
    if old_status:
        old_label = LoanApplication.Status(old_status).label
        new_label = application.get_status_display()
        lines.append(f"Status: {old_label} → {new_label}")
    else:
        lines.append(f"Status: {application.get_status_display()}")

    lines.extend(
        [
            f"Product: {product_name}",
            f"Requested amount: {_format_money(application.requested_amount)}",
            f"Term: {application.term_months} months",
            f"Purpose: {application.purpose}",
            f"Submitted: {application.created_at:%A, %d %B %Y at %H:%M UTC}",
            f"Last updated: {application.updated_at:%A, %d %B %Y at %H:%M UTC}",
            "",
            "ACCOUNT",
            "────────────────────────────────────────",
            f"Name: {user.full_name or user.display_name}",
            f"Email: {user.email}",
            "",
            "NEED ASSISTANCE?",
            "────────────────────────────────────────",
            "Our support team is here to help with any questions about your loan application.",
            f"Email: {SUPPORT_EMAIL}",
            f"Reference to quote: {application.reference_code}",
            "Please include your registered email address and the reference code above when you contact us.",
            "",
            "WHAT YOU SHOULD DO",
            "────────────────────────────────────────",
            "1. Sign in to your PennyCredit dashboard to view your loan status.",
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
) -> None:
    if application.status not in NOTIFY_STATUSES:
        return
    if old_status == application.status:
        return

    user = application.user
    if not user.email:
        return

    status_prefix = STATUS_SUBJECTS.get(application.status, "Loan application update")
    subject = (
        f"PennyCredit — {status_prefix} ({application.reference_code})"
    )
    message = _build_email_body(application, old_status=old_status)

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
