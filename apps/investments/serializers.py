from decimal import Decimal

from rest_framework import serializers

from apps.wallets.models import Wallet

from .duration_utils import maturity_datetime
from .models import InvestmentPlan, UserInvestment


def calculate_expected_return(amount: Decimal, plan: InvestmentPlan) -> Decimal:
    if plan.return_type == "percent":
        return (amount * plan.return_value / Decimal("100")).quantize(Decimal("0.01"))
    return plan.return_value.quantize(Decimal("0.01"))


class InvestmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentPlan
        fields = [
            "id",
            "slug",
            "name",
            "minimum_amount",
            "maximum_amount",
            "return_type",
            "return_value",
            "duration_label",
            "returns_capital",
            "is_active",
            "display_order",
        ]


class UserInvestmentSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    plan_slug = serializers.CharField(source="plan.slug", read_only=True)

    class Meta:
        model = UserInvestment
        fields = [
            "id",
            "plan",
            "plan_name",
            "plan_slug",
            "reference_code",
            "invested_amount",
            "expected_return_amount",
            "status",
            "matures_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reference_code",
            "status",
            "expected_return_amount",
            "created_at",
            "updated_at",
        ]


class UserInvestmentCreateSerializer(serializers.Serializer):
    plan = serializers.PrimaryKeyRelatedField(queryset=InvestmentPlan.objects.filter(is_active=True))
    invested_amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("1"))
    transaction_pin = serializers.CharField(min_length=4, max_length=4, write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        plan = attrs["plan"]
        amount = attrs["invested_amount"]
        pin = attrs["transaction_pin"]

        if not user.has_transaction_pin:
            raise serializers.ValidationError(
                {"transaction_pin": "Set a transaction PIN before investing."}
            )
        if not user.check_transaction_pin(pin):
            raise serializers.ValidationError({"transaction_pin": "Incorrect transaction PIN."})

        if amount < plan.minimum_amount:
            raise serializers.ValidationError(
                {"invested_amount": f"Minimum investment is ${plan.minimum_amount}."}
            )
        if amount > plan.maximum_amount:
            raise serializers.ValidationError(
                {"invested_amount": f"Maximum investment is ${plan.maximum_amount}."}
            )

        wallet = (
            Wallet.objects.filter(user=user, currency_code="USD").first()
            or Wallet.objects.filter(user=user).first()
        )
        if not wallet:
            raise serializers.ValidationError({"invested_amount": "No wallet found."})
        if wallet.balance < amount:
            raise serializers.ValidationError({"invested_amount": "Insufficient wallet balance."})

        attrs["_wallet"] = wallet
        return attrs

    def create(self, validated_data):
        from apps.core.utils import generate_reference_code

        user = self.context["request"].user
        plan = validated_data["plan"]
        amount = validated_data["invested_amount"]
        wallet = validated_data.pop("_wallet")
        validated_data.pop("transaction_pin")

        wallet.balance -= amount
        wallet.save(update_fields=["balance", "updated_at"])

        expected = calculate_expected_return(amount, plan)
        investment = UserInvestment.objects.create(
            user=user,
            plan=plan,
            reference_code=generate_reference_code("INV"),
            invested_amount=amount,
            expected_return_amount=expected,
            status=UserInvestment.Status.ACTIVE,
            matures_at=maturity_datetime(plan.duration_label),
        )
        return investment
