from decimal import Decimal

from django.db.models import QuerySet

from apps.wallets.models import Wallet


def get_user_currency(user) -> str:
    return getattr(user, "currency_code", None) or "USD"


def _pick_primary_wallet(wallets: QuerySet[Wallet] | list[Wallet]) -> Wallet:
    """Wallet that holds the user's main fiat balance."""
    wallet_list = list(wallets)
    if not wallet_list:
        raise ValueError("No wallets to pick from")
    return max(wallet_list, key=lambda w: (w.balance, w.updated_at, w.pk))


def sync_user_wallet_currency(user) -> Wallet | None:
    """
    When account currency changes, relabel the primary wallet (keep balance).
    Does not convert amounts — only updates the currency code on the same wallet.
    """
    target = get_user_currency(user)
    wallets = Wallet.objects.filter(user=user)
    if not wallets.exists():
        return Wallet.objects.create(
            user=user,
            currency_code=target,
            balance=Decimal("0"),
        )

    primary = _pick_primary_wallet(wallets)
    if primary.currency_code == target:
        return primary

    conflict = (
        Wallet.objects.filter(user=user, currency_code=target)
        .exclude(pk=primary.pk)
        .first()
    )
    if conflict:
        if conflict.balance == 0:
            conflict.delete()
        elif primary.balance == 0:
            return conflict
        else:
            # Two funded wallets — keep highest balance as primary for display
            return primary

    primary.currency_code = target
    primary.save(update_fields=["currency_code", "updated_at"])
    return primary


def get_or_create_primary_wallet(user) -> Wallet:
    """
    Primary wallet for dashboard and transfers.
    Uses the user's balance wallet and aligns its currency_code with user.currency_code.
    """
    wallets = Wallet.objects.filter(user=user)
    if not wallets.exists():
        return Wallet.objects.create(
            user=user,
            currency_code=get_user_currency(user),
            balance=Decimal("0"),
        )

    primary = _pick_primary_wallet(wallets)
    target = get_user_currency(user)
    if primary.currency_code != target:
        return sync_user_wallet_currency(user) or primary
    return primary
