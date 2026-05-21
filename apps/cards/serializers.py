from datetime import date
from decimal import Decimal

from rest_framework import serializers

from apps.wallets.models import Wallet

from .card_utils import format_pan, generate_card_number, generate_cvv, mask_pan
from .models import NEW_CARD_REQUEST_FEE, CardRequest, CardTransaction, VirtualCard


class VirtualCardSerializer(serializers.ModelSerializer):
    masked_card_number = serializers.SerializerMethodField()

    class Meta:
        model = VirtualCard
        fields = [
            "id",
            "card_name",
            "cardholder_name",
            "network",
            "theme",
            "masked_card_number",
            "last_four_digits",
            "expiry_date",
            "is_frozen",
            "spending_limit",
            "monthly_spent_amount",
            "balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "cardholder_name",
            "masked_card_number",
            "last_four_digits",
            "expiry_date",
            "monthly_spent_amount",
            "balance",
            "created_at",
            "updated_at",
        ]

    def get_masked_card_number(self, obj):
        return mask_pan(obj.card_number, obj.last_four_digits)


class CardSensitiveRevealSerializer(serializers.Serializer):
    transaction_pin = serializers.CharField(min_length=4, max_length=4, write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        pin = attrs["transaction_pin"]
        if not user.has_transaction_pin:
            raise serializers.ValidationError(
                {"transaction_pin": "Set a transaction PIN first."}
            )
        if not user.check_transaction_pin(pin):
            raise serializers.ValidationError({"transaction_pin": "Incorrect transaction PIN."})
        return attrs


class CardRequestSerializer(serializers.ModelSerializer):
    issued_card_detail = VirtualCardSerializer(source="issued_card", read_only=True)

    class Meta:
        model = CardRequest
        fields = [
            "id",
            "card_name",
            "theme",
            "issuance_fee",
            "status",
            "issued_card",
            "issued_card_detail",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "issuance_fee",
            "status",
            "issued_card",
            "issued_card_detail",
            "created_at",
            "updated_at",
        ]


class CardRequestCreateSerializer(serializers.ModelSerializer):
    network = serializers.ChoiceField(choices=VirtualCard.Network.choices)
    spending_limit = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("500"))
    transaction_pin = serializers.CharField(write_only=True, min_length=4, max_length=4)

    class Meta:
        model = CardRequest
        fields = [
            "card_name",
            "theme",
            "network",
            "spending_limit",
            "transaction_pin",
        ]

    def validate(self, attrs):
        user = self.context["request"].user
        pin = attrs.get("transaction_pin", "")
        if not user.has_transaction_pin:
            raise serializers.ValidationError(
                {"transaction_pin": "Set a transaction PIN before requesting a card."}
            )
        if not user.check_transaction_pin(pin):
            raise serializers.ValidationError({"transaction_pin": "Incorrect transaction PIN."})

        wallet = (
            Wallet.objects.filter(user=user, currency_code="USD").first()
            or Wallet.objects.filter(user=user).first()
        )
        if not wallet:
            raise serializers.ValidationError({"card_name": "No wallet found."})
        if wallet.balance < NEW_CARD_REQUEST_FEE:
            raise serializers.ValidationError(
                {"card_name": f"Insufficient balance for the ${NEW_CARD_REQUEST_FEE} issuance fee."}
            )
        attrs["_wallet"] = wallet
        return attrs

    def create(self, validated_data):
        validated_data.pop("transaction_pin")
        network = validated_data.pop("network")
        spending_limit = validated_data.pop("spending_limit")
        wallet = validated_data.pop("_wallet")
        user = self.context["request"].user

        wallet.balance -= NEW_CARD_REQUEST_FEE
        wallet.save(update_fields=["balance", "updated_at"])

        today = date.today()
        expiry = f"{today.month:02d}/{(today.year + 3) % 100:02d}"
        pan = generate_card_number()
        last_four = pan[-4:]
        holder = (
            user.full_name or f"{user.first_name} {user.last_name}".strip() or user.email
        ).upper()

        card = VirtualCard.objects.create(
            user=user,
            card_name=validated_data["card_name"],
            cardholder_name=holder[:128],
            network=network,
            theme=validated_data.get("theme") or VirtualCard.Theme.TEAL_GOLD,
            card_number=pan,
            last_four_digits=last_four,
            expiry_date=expiry,
            cvv=generate_cvv(),
            spending_limit=spending_limit,
        )

        request_obj = CardRequest.objects.create(
            user=user,
            card_name=validated_data["card_name"],
            theme=card.theme,
            issuance_fee=NEW_CARD_REQUEST_FEE,
            status="issued",
            issued_card=card,
        )
        return request_obj


class CardTransactionSerializer(serializers.ModelSerializer):
    card_name = serializers.CharField(source="card.card_name", read_only=True)

    class Meta:
        model = CardTransaction
        fields = [
            "id",
            "card",
            "card_name",
            "merchant_name",
            "amount",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
