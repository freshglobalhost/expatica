from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class InvestmentPlan(BaseModel):
    slug = models.SlugField(unique=True, max_length=64)
    name = models.CharField(max_length=128)
    minimum_amount = models.DecimalField(max_digits=14, decimal_places=2)
    maximum_amount = models.DecimalField(max_digits=14, decimal_places=2)
    return_type = models.CharField(
        max_length=10,
        choices=[("percent", "Percent"), ("fixed", "Fixed")],
    )
    return_value = models.DecimalField(max_digits=14, decimal_places=2)
    duration_label = models.CharField(max_length=64)
    returns_capital = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "minimum_amount"]

    def __str__(self):
        return self.name


class UserInvestment(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        MATURED = "matured", "Matured"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investments",
    )
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.PROTECT, related_name="user_investments")
    reference_code = models.CharField(max_length=32, unique=True, db_index=True)
    invested_amount = models.DecimalField(max_digits=14, decimal_places=2)
    expected_return_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    matures_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]
