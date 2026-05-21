from django.contrib import admin

from .models import AutoSaveRule, LockedSavingsAccount, SavingsGoal, SavingsTransaction


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ("goal_name", "user", "target_amount", "saved_amount")


@admin.register(LockedSavingsAccount)
class LockedSavingsAccountAdmin(admin.ModelAdmin):
    list_display = ("account_name", "user", "locked_amount", "unlocks_on")


@admin.register(AutoSaveRule)
class AutoSaveRuleAdmin(admin.ModelAdmin):
    list_display = ("rule_name", "user", "is_enabled", "total_saved_amount")


@admin.register(SavingsTransaction)
class SavingsTransactionAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "user", "transaction_type", "amount", "created_at")
