from django.conf import settings
from django.db import models

from apps.core.models import BaseModel
from apps.wallets.currencies import CURRENCY_CHOICES


class Wallet(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallets",
    )
    currency_code = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="USD",
    )
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    btc_balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    eth_balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    usdt_balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    sol_balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)

    class Meta:
        unique_together = [("user", "currency_code")]
        ordering = ["currency_code"]

    def __str__(self):
        return f"{self.user_id} · {self.currency_code} ({self.balance})"

    def add_crypto_balance(self, symbol: str, amount) -> None:
        field_map = {
            "BTC": "btc_balance",
            "ETH": "eth_balance",
            "USDT": "usdt_balance",
            "SOL": "sol_balance",
        }
        field = field_map.get(symbol.upper())
        if not field:
            return
        current = getattr(self, field)
        setattr(self, field, current + amount)
        self.save(update_fields=[field, "updated_at"])
