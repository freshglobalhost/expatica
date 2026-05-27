from decimal import Decimal

from apps.wallets.models import Wallet


def get_user_currency(user) -> str:
    return getattr(user, "currency_code", None) or "USD"


def get_or_create_primary_wallet(user) -> Wallet:
    """Wallet matching the user's account currency (admin-configurable)."""
    currency = get_user_currency(user)
    wallet, _ = Wallet.objects.get_or_create(
        user=user,
        currency_code=currency,
        defaults={"balance": Decimal("0")},
    )
    return wallet
