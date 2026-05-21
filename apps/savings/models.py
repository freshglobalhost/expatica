from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class SavingsGoal(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="savings_goals",
    )
    goal_name = models.CharField(max_length=128)
    target_amount = models.DecimalField(max_digits=14, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    target_date_label = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ["goal_name"]


class LockedSavingsAccount(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="locked_savings",
    )
    account_name = models.CharField(max_length=128)
    locked_amount = models.DecimalField(max_digits=14, decimal_places=2)
    interest_rate_label = models.CharField(max_length=32)
    unlocks_on = models.DateField()

    class Meta:
        ordering = ["unlocks_on"]


class AutoSaveRule(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="auto_save_rules",
    )
    rule_name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True)
    is_enabled = models.BooleanField(default=True)
    total_saved_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    rule_settings = models.JSONField(default=dict)

    class Meta:
        ordering = ["rule_name"]


class SavingsTransaction(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="savings_transactions",
    )
    reference_code = models.CharField(max_length=32, unique=True, db_index=True)
    transaction_type = models.CharField(max_length=32)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    goal = models.ForeignKey(
        SavingsGoal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    class Meta:
        ordering = ["-created_at"]
