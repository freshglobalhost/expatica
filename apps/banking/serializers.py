from decimal import Decimal

from django.db import transaction as db_transaction
from rest_framework import serializers

from apps.transactions.models import Transaction
from apps.wallets.services import get_or_create_primary_wallet

from .models import Transfer, TransferMethod
from .transfer_validation import (
    INVALID_ROUTING_MESSAGE,
    INVALID_SWIFT_MESSAGE,
    is_valid_transfer_code,
)


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
            "kind",
            "amount",
            "fee_amount",
            "status",
            "reference_code",
            "recipient_details",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reference_code",
            "status",
            "fee_amount",
            "kind",
            "created_at",
            "updated_at",
        ]


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
            kind = self.context.get("payout_kind", Transfer.Kind.TRANSFER)
            noun = "withdrawal" if kind == Transfer.Kind.WITHDRAWAL else "transfer"
            raise serializers.ValidationError(f"Minimum {noun} amount is 1.00.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        pin = attrs.pop("transaction_pin", "")
        kind = self.context.get("payout_kind", Transfer.Kind.TRANSFER)
        noun = "withdrawal" if kind == Transfer.Kind.WITHDRAWAL else "transfer"

        if not user.has_transaction_pin:
            raise serializers.ValidationError(
                {"transaction_pin": f"Set a transaction PIN in settings before submitting a {noun}."}
            )
        if not user.check_transaction_pin(pin):
            raise serializers.ValidationError({"transaction_pin": "Invalid transaction PIN."})

        method = attrs.get("method")
        details = attrs.get("recipient_details") or {}
        if method:
            if method.slug == "local":
                routing = details.get("routing_number", "")
                if not is_valid_transfer_code(routing):
                    raise serializers.ValidationError(
                        {"recipient_details": INVALID_ROUTING_MESSAGE}
                    )
            elif method.slug == "wire":
                swift = details.get("swift_bic", "")
                if not is_valid_transfer_code(swift):
                    raise serializers.ValidationError(
                        {"recipient_details": INVALID_SWIFT_MESSAGE}
                    )

        wallet = get_or_create_primary_wallet(user)
        if wallet.balance < attrs["amount"]:
            raise serializers.ValidationError({"amount": "Insufficient wallet balance."})

        attrs["_wallet"] = wallet
        return attrs

    def to_representation(self, instance):
        return TransferSerializer(instance, context=self.context).data

    def create(self, validated_data):
        wallet = validated_data.pop("_wallet")
        user = self.context["request"].user
        reference_code = self.context["reference_code"]
        method = validated_data["method"]
        amount = validated_data["amount"]
        kind = self.context.get("payout_kind", Transfer.Kind.TRANSFER)
        is_withdrawal = kind == Transfer.Kind.WITHDRAWAL
        category = (
            Transaction.Category.WITHDRAWAL if is_withdrawal else Transaction.Category.TRANSFER
        )
        label = "Withdrawal" if is_withdrawal else "Transfer"

        with db_transaction.atomic():
            wallet = type(wallet).objects.select_for_update().get(pk=wallet.pk)
            if wallet.balance < amount:
                raise serializers.ValidationError({"amount": "Insufficient wallet balance."})

            payout = Transfer.objects.create(
                user=user,
                reference_code=reference_code,
                status=Transfer.Status.PENDING,
                kind=kind,
                **validated_data,
            )
            wallet.balance -= amount
            wallet.save(update_fields=["balance", "updated_at"])

            Transaction.objects.create(
                user=user,
                direction=Transaction.Direction.DEBIT,
                category=category,
                amount=amount,
                currency_code=wallet.currency_code,
                status=Transaction.Status.PENDING,
                reference_code=reference_code,
                description=f"{label} · {method.name}",
                counterparty_name=method.name,
            )

        return payout
