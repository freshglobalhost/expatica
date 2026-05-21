from django.conf import settings
from django.db import models

from apps.core.models import BaseModel
from apps.wallets.currencies import CURRENCY_CHOICES


class Transaction(BaseModel):
    class Direction(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    class Category(models.TextChoices):
        TRANSFER = "transfer", "Transfer"
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        LOAN = "loan", "Loan"
        CARD = "card", "Card"
        INVESTMENT = "investment", "Investment"
        SAVINGS = "savings", "Savings"
        FEE = "fee", "Fee"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    class CryptoSymbol(models.TextChoices):
        BTC = "BTC", "Bitcoin"
        ETH = "ETH", "Ethereum"
        USDT = "USDT", "Tether"
        SOL = "SOL", "Solana"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    direction = models.CharField(max_length=10, choices=Direction.choices)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency_code = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reference_code = models.CharField(max_length=64, unique=True, db_index=True)
    description = models.CharField(max_length=255, blank=True)
    counterparty_name = models.CharField(max_length=128, blank=True)
    crypto_symbol = models.CharField(
        max_length=8,
        choices=CryptoSymbol.choices,
        blank=True,
        null=True,
    )
    crypto_amount = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        null=True,
        blank=True,
    )
    transaction_hash = models.CharField(max_length=128, blank=True)
    proof_image = models.ImageField(
        upload_to="transactions/deposit_proofs/%Y/%m/",
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "category", "status"]),
        ]

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            old_status = (
                Transaction.objects.filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )
        super().save(*args, **kwargs)
        if (
            self.crypto_symbol
            and self.category == self.Category.DEPOSIT
            and self.status == self.Status.COMPLETED
            and old_status != self.Status.COMPLETED
            and self.crypto_amount
        ):
            self._credit_crypto_to_wallet()

    def _credit_crypto_to_wallet(self):
        from apps.wallets.models import Wallet

        wallet = (
            Wallet.objects.filter(user=self.user, currency_code=self.currency_code).first()
            or Wallet.objects.filter(user=self.user).first()
        )
        if wallet:
            wallet.add_crypto_balance(self.crypto_symbol, self.crypto_amount)
