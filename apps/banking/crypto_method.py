"""Ensure the crypto withdrawal method exists without a schema migration."""

from apps.banking.models import TransferMethod

CRYPTO_METHOD_SLUG = "crypto"


def ensure_crypto_transfer_method() -> TransferMethod:
    method, _created = TransferMethod.objects.get_or_create(
        slug=CRYPTO_METHOD_SLUG,
        defaults={
            "name": "Crypto Withdrawal",
            "category": "crypto",
            "display_order": 9,
            "is_active": True,
        },
    )
    return method
