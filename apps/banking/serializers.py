from decimal import Decimal

from rest_framework import serializers

from apps.transactions.models import Transaction
from apps.wallets.models import Wallet

from .models import Transfer, TransferMethod


class TransferMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferMethod
        fields = [
            "id",
            "slug",
            "name",
            "category",
            "display_order",
            "is_active",
        ]


class TransferSerializer(serializers.ModelSerializer):
    method_name = serializers.CharField(source="method.name", read_only=True)
    method_slug = serializers.CharField(source="method.slug", read_only=True)

    class Meta:
        model = Transfer
        fields = [
            "id",
            "method",
            "method_name",
            "method_slug",
            "amount",
            "fee_amount",
            "status",
            "reference_code",
            "recipient_details",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reference_code", "status", "fee_amount", "created_at", "updated_at"]


class TransferCreateSerializer(serializers.ModelSerializer):
    transaction_pin = serializers.CharField(write_only=True, max_length=4, min_length=4)

    class Meta:
        model = Transfer
        fields = [
            "method",
            "amount",
            "recipient_details",
            "note",
            "transaction_pin",
        ]

    def validate_amount(self, value):
        if value < Decimal("1"):
            raise serializers.ValidationError("Minimum transfer amount is 1.00.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        pin = attrs.pop("transaction_pin", "")

        if not user.has_transaction_pin:
            raise serializers.ValidationError(
                {"transaction_pin": "Set a transaction PIN in settings before sending money."}
            )
        if not user.check_transaction_pin(pin):
            raise serializers.ValidationError({"transaction_pin": "Invalid transaction PIN."})

        wallet = (
            Wallet.objects.filter(user=user, currency_code="USD").first()
            or Wallet.objects.filter(user=user).order_by("currency_code").first()
        )
        if not wallet:
            raise serializers.ValidationError({"amount": "No wallet found for your account."})
        if wallet.balance < attrs["amount"]:
            raise serializers.ValidationError({"amount": "Insufficient wallet balance."})

        attrs["_wallet"] = wallet
        return attrs

    def create(self, validated_data):
        wallet = validated_data.pop("_wallet")
        user = self.context["request"].user
        reference_code = self.context["reference_code"]
        method = validated_data["method"]
        amount = validated_data["amount"]

        transfer = Transfer.objects.create(
            user=user,
            reference_code=reference_code,
            status=Transfer.Status.PENDING,
            **validated_data,
        )

        wallet.balance -= amount
        wallet.save(update_fields=["balance", "updated_at"])

        Transaction.objects.create(
            user=user,
            direction=Transaction.Direction.DEBIT,
            category=Transaction.Category.TRANSFER,
            amount=amount,
            currency_code=wallet.currency_code,
            status=Transaction.Status.PENDING,
            reference_code=reference_code,
            description=f"Transfer · {method.name}",
            counterparty_name=method.name,
        )

        return transfer
