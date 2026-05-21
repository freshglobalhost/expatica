from rest_framework import serializers

from .models import AutoSaveRule, LockedSavingsAccount, SavingsGoal, SavingsTransaction


class SavingsGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsGoal
        fields = [
            "id",
            "goal_name",
            "target_amount",
            "saved_amount",
            "target_date_label",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "saved_amount", "created_at", "updated_at"]


class LockedSavingsAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = LockedSavingsAccount
        fields = [
            "id",
            "account_name",
            "locked_amount",
            "interest_rate_label",
            "unlocks_on",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AutoSaveRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoSaveRule
        fields = [
            "id",
            "rule_name",
            "description",
            "is_enabled",
            "total_saved_amount",
            "rule_settings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_saved_amount", "created_at", "updated_at"]


class SavingsTransactionSerializer(serializers.ModelSerializer):
    goal_name = serializers.CharField(source="goal.goal_name", read_only=True, allow_null=True)

    class Meta:
        model = SavingsTransaction
        fields = [
            "id",
            "reference_code",
            "transaction_type",
            "amount",
            "goal",
            "goal_name",
            "created_at",
        ]
        read_only_fields = ["id", "reference_code", "created_at"]
