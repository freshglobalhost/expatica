from django.conf import settings
from django.db import models

from apps.core.models import BaseModel

NEW_CARD_REQUEST_FEE = 5


class VirtualCard(BaseModel):
    class Network(models.TextChoices):
        VISA = "visa", "Visa"
        MASTERCARD = "mastercard", "Mastercard"

    class Theme(models.TextChoices):
        TEAL_GOLD = "teal-gold", "Teal & Gold"
        MIDNIGHT = "midnight", "Midnight"
        SUNSET = "sunset", "Sunset"
        OCEAN = "ocean", "Ocean"
        ROYAL = "royal", "Royal"
        CARBON = "carbon", "Carbon"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="virtual_cards",
    )
    card_name = models.CharField(max_length=64)
    cardholder_name = models.CharField(max_length=128, blank=True)
    network = models.CharField(max_length=16, choices=Network.choices)
    theme = models.CharField(max_length=16, choices=Theme.choices, default=Theme.TEAL_GOLD)
    card_number = models.CharField(max_length=19, blank=True, db_index=True)
    last_four_digits = models.CharField(max_length=4)
    expiry_date = models.CharField(max_length=7)
    cvv = models.CharField(max_length=4, blank=True)
    is_frozen = models.BooleanField(default=False)
    spending_limit = models.DecimalField(max_digits=14, decimal_places=2)
    monthly_spent_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]


class CardRequest(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="card_requests",
    )
    card_name = models.CharField(max_length=64)
    theme = models.CharField(max_length=16, default="teal-gold")
    issuance_fee = models.DecimalField(max_digits=14, decimal_places=2, default=NEW_CARD_REQUEST_FEE)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("issued", "Issued"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    issued_card = models.ForeignKey(
        VirtualCard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="request",
    )


class CardTransaction(BaseModel):
    card = models.ForeignKey(VirtualCard, on_delete=models.CASCADE, related_name="transactions")
    merchant_name = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        ordering = ["-created_at"]
