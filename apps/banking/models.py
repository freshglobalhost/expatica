from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class TransferMethod(BaseModel):
    slug = models.SlugField(unique=True, max_length=32)
    name = models.CharField(max_length=64)
    category = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class Transfer(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    class Kind(models.TextChoices):
        TRANSFER = "transfer", "Transfer"
        WITHDRAWAL = "withdrawal", "Withdrawal"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transfers",
    )
    method = models.ForeignKey(TransferMethod, on_delete=models.PROTECT, related_name="transfers")
    kind = models.CharField(
        max_length=20,
        choices=Kind.choices,
        default=Kind.TRANSFER,
        db_index=True,
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reference_code = models.CharField(max_length=64, unique=True, db_index=True)
    recipient_details = models.JSONField(default=dict)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
