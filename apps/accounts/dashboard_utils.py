from datetime import timedelta

from django.utils import timezone

from apps.cards.models import VirtualCard
from apps.loans.models import Loan, LoanRepayment
from apps.transactions.models import Transaction


def build_dashboard_notifications(user) -> list[dict]:
    items: list[dict] = []
    today = timezone.now().date()
    week_ahead = today + timedelta(days=7)

    for tx in Transaction.objects.filter(
        user=user, status=Transaction.Status.PENDING
    ).order_by("-created_at")[:3]:
        items.append(
            {
                "id": f"tx-pending-{tx.id}",
                "title": "Transaction pending",
                "message": tx.description or f"{tx.get_category_display()} · {tx.reference_code}",
                "created_at": tx.created_at.isoformat(),
                "unread": True,
                "type": "warning",
            }
        )

    for tx in Transaction.objects.filter(
        user=user,
        category=Transaction.Category.DEPOSIT,
        status=Transaction.Status.COMPLETED,
    ).order_by("-created_at")[:2]:
        amount_label = str(tx.amount)
        if tx.crypto_symbol and tx.crypto_amount:
            amount_label = f"{tx.crypto_amount} {tx.crypto_symbol}"
        items.append(
            {
                "id": f"tx-deposit-{tx.id}",
                "title": "Deposit received",
                "message": tx.description or f"Deposit of {amount_label} credited",
                "created_at": tx.created_at.isoformat(),
                "unread": False,
                "type": "success",
            }
        )

    for rep in (
        LoanRepayment.objects.filter(
            loan__user=user,
            loan__status=Loan.Status.ACTIVE,
            paid_on__isnull=True,
            due_on__lte=week_ahead,
        )
        .select_related("loan", "loan__product")
        .order_by("due_on")[:3]
    ):
        items.append(
            {
                "id": f"repayment-{rep.id}",
                "title": "Loan payment due soon",
                "message": (
                    f"{rep.loan.product.name} payment of ${rep.amount} "
                    f"due {rep.due_on.strftime('%b %d, %Y')}"
                ),
                "created_at": rep.created_at.isoformat(),
                "unread": True,
                "type": "warning",
            }
        )

    for card in VirtualCard.objects.filter(user=user, is_frozen=True).order_by("-updated_at")[:1]:
        items.append(
            {
                "id": f"card-frozen-{card.id}",
                "title": "Card frozen",
                "message": f"{card.card_name} ·••• {card.last_four_digits} is frozen",
                "created_at": card.updated_at.isoformat(),
                "unread": True,
                "type": "info",
            }
        )

    items.sort(key=lambda x: x["created_at"], reverse=True)
    return items[:10]
