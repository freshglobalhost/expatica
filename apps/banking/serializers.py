from decimal import Decimal, InvalidOperation, ROUND_DOWN, ROUND_HALF_UP

from django.db import transaction as db_transaction
from rest_framework import serializers

from apps.transactions.crypto_assets import get_crypto_asset
from apps.transactions.models import Transaction
from apps.wallets.services import get_or_create_primary_wallet

from .crypto_method import CRYPTO_METHOD_SLUG
from .models import Transfer, TransferMethod
from .transfer_validation import (
    INVALID_ROUTING_MESSAGE,
    INVALID_SWIFT_MESSAGE,
    INVALID_WITHDRAWAL_ACCESS_CODE_MESSAGE,
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
    kind = serializers.SerializerMethodField()

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

    def get_kind(self, obj):
        code = obj.reference_code or ""
        return "withdrawal" if code.startswith("WD-") else "transfer"


def _detail_value(details: dict, *keys: str) -> str:
    for key in keys:
        value = details.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _parse_crypto_amount(raw) -> Decimal | None:
    if raw is None or raw == "":
        return None
    try:
        amount = Decimal(str(raw))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if amount <= 0:
        return None
    return amount.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)


class TransferCreateSerializer(serializers.ModelSerializer):
    transaction_pin = serializers.CharField(write_only=True, max_length=4, min_length=4)
    # Crypto withdrawals use up to 8 decimal places; fiat is quantized to 2 on save.
    amount = serializers.DecimalField(max_digits=18, decimal_places=8)

    class Meta:
        model = Transfer
        fields = [
            "method",
            "amount",
            "recipient_details",
            "note",
            "transaction_pin",
        ]

    def _is_withdrawal(self):
        return bool(self.context.get("is_withdrawal"))

    def _noun(self):
        return "withdrawal" if self._is_withdrawal() else "transfer"

    def validate_amount(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def _validate_crypto_withdrawal(self, attrs, details: dict, wallet):
        if not self._is_withdrawal():
            raise serializers.ValidationError(
                {"method": "Crypto withdrawals must be submitted via /banking/withdrawals/."}
            )

        symbol = _detail_value(details, "crypto_symbol").upper()
        asset = get_crypto_asset(symbol)
        if not asset:
            raise serializers.ValidationError(
                {"recipient_details": "Select a supported cryptocurrency wallet."}
            )

        access_code = _detail_value(
            details, "withdrawal_access_code", "access_code"
        )
        if not is_valid_transfer_code(access_code):
            raise serializers.ValidationError(
                {"recipient_details": INVALID_WITHDRAWAL_ACCESS_CODE_MESSAGE}
            )

        destination = _detail_value(
            details, "destination_address", "wallet_address", "crypto_address"
        )
        if not destination:
            raise serializers.ValidationError(
                {"recipient_details": "Enter the destination crypto address."}
            )

        crypto_amount = _parse_crypto_amount(
            details.get("crypto_amount") or attrs.get("amount")
        )
        if crypto_amount is None:
            raise serializers.ValidationError({"amount": "Enter a valid crypto amount."})

        minimum = asset["minimum_deposit_amount"]
        if crypto_amount < minimum:
            raise serializers.ValidationError(
                {"amount": f"Minimum withdrawal for {symbol} is {minimum}."}
            )

        available = wallet.get_crypto_balance(symbol)
        if available is None or available < crypto_amount:
            raise serializers.ValidationError(
                {"amount": f"Insufficient {symbol} wallet balance."}
            )

        details["crypto_symbol"] = symbol
        details["crypto_amount"] = format(crypto_amount, "f")
        details["destination_address"] = destination
        attrs["recipient_details"] = details
        # Transfer.amount is decimal_places=2; keep full precision on Transaction.crypto_amount.
        attrs["amount"] = crypto_amount.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        attrs["_crypto_symbol"] = symbol
        attrs["_crypto_amount"] = crypto_amount
        attrs["_destination_address"] = destination
        return attrs

    def validate(self, attrs):
        user = self.context["request"].user
        pin = attrs.pop("transaction_pin", "")
        noun = self._noun()

        if not user.has_transaction_pin:
            raise serializers.ValidationError(
                {"transaction_pin": f"Set a transaction PIN in settings before submitting a {noun}."}
            )
        if not user.check_transaction_pin(pin):
            raise serializers.ValidationError({"transaction_pin": "Invalid transaction PIN."})

        method = attrs.get("method")
        details = dict(attrs.get("recipient_details") or {})
        wallet = get_or_create_primary_wallet(user)

        if method and method.slug == CRYPTO_METHOD_SLUG:
            attrs["_wallet"] = wallet
            return self._validate_crypto_withdrawal(attrs, details, wallet)

        if attrs["amount"] < Decimal("1"):
            raise serializers.ValidationError(
                {"amount": f"Minimum {noun} amount is 1.00."}
            )
        attrs["amount"] = attrs["amount"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

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

        if wallet.balance < attrs["amount"]:
            raise serializers.ValidationError({"amount": "Insufficient wallet balance."})

        attrs["recipient_details"] = details
        attrs["_wallet"] = wallet
        attrs["_crypto_symbol"] = None
        attrs["_crypto_amount"] = None
        attrs["_destination_address"] = None
        return attrs

    def to_representation(self, instance):
        return TransferSerializer(instance, context=self.context).data

    def create(self, validated_data):
        wallet = validated_data.pop("_wallet")
        crypto_symbol = validated_data.pop("_crypto_symbol", None)
        crypto_amount = validated_data.pop("_crypto_amount", None)
        destination_address = validated_data.pop("_destination_address", None)
        user = self.context["request"].user
        reference_code = self.context["reference_code"]
        method = validated_data["method"]
        amount = validated_data["amount"]
        is_withdrawal = self._is_withdrawal()
        category = (
            Transaction.Category.WITHDRAWAL if is_withdrawal else Transaction.Category.TRANSFER
        )
        label = "Withdrawal" if is_withdrawal else "Transfer"

        with db_transaction.atomic():
            wallet = type(wallet).objects.select_for_update().get(pk=wallet.pk)

            if crypto_symbol:
                available = wallet.get_crypto_balance(crypto_symbol)
                if available is None or available < crypto_amount:
                    raise serializers.ValidationError(
                        {"amount": f"Insufficient {crypto_symbol} wallet balance."}
                    )
            elif wallet.balance < amount:
                raise serializers.ValidationError({"amount": "Insufficient wallet balance."})

            payout = Transfer.objects.create(
                user=user,
                reference_code=reference_code,
                status=Transfer.Status.PENDING,
                **validated_data,
            )

            tx_kwargs = {
                "user": user,
                "direction": Transaction.Direction.DEBIT,
                "category": category,
                "currency_code": wallet.currency_code,
                "status": Transaction.Status.PENDING,
                "reference_code": reference_code,
                "description": f"{label} · {method.name}",
                "counterparty_name": method.name,
            }

            if crypto_symbol:
                wallet.debit_crypto_balance(crypto_symbol, crypto_amount)
                tx_kwargs["amount"] = Decimal("0")
                tx_kwargs["crypto_symbol"] = crypto_symbol
                tx_kwargs["crypto_amount"] = crypto_amount
                tx_kwargs["description"] = f"{label} · {method.name} · {crypto_symbol}"
                tx_kwargs["counterparty_name"] = (destination_address or method.name)[:128]
            else:
                wallet.balance -= amount
                wallet.save(update_fields=["balance", "updated_at"])
                tx_kwargs["amount"] = amount

            Transaction.objects.create(**tx_kwargs)

        return payout
