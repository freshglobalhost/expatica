from decimal import Decimal

from rest_framework import serializers

from apps.transactions.crypto_assets import CRYPTO_ASSETS, CRYPTO_SYMBOLS

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    proof_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "direction",
            "category",
            "amount",
            "currency_code",
            "status",
            "reference_code",
            "description",
            "counterparty_name",
            "crypto_symbol",
            "crypto_amount",
            "transaction_hash",
            "proof_image",
            "proof_image_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reference_code",
            "status",
            "proof_image_url",
            "created_at",
            "updated_at",
        ]

    def get_proof_image_url(self, obj):
        if not obj.proof_image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.proof_image.url)
        return obj.proof_image.url


class CryptoDepositCreateSerializer(serializers.Serializer):
    crypto_symbol = serializers.ChoiceField(choices=sorted(CRYPTO_SYMBOLS))
    crypto_amount = serializers.DecimalField(max_digits=18, decimal_places=8, min_value=Decimal("0"))
    transaction_hash = serializers.CharField(required=False, allow_blank=True, max_length=128)
    proof_image = serializers.ImageField(required=False, allow_null=True)
    currency_code = serializers.CharField(required=False, max_length=3, default="USD")

    def validate_crypto_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_currency_code(self, value):
        from apps.wallets.currencies import CURRENCY_CODES

        if value not in CURRENCY_CODES:
            raise serializers.ValidationError("Unsupported currency code.")
        return value

    def validate(self, attrs):
        symbol = attrs["crypto_symbol"]
        amount = attrs["crypto_amount"]
        asset = next((a for a in CRYPTO_ASSETS if a["symbol"] == symbol), None)
        if asset and amount < asset["minimum_deposit_amount"]:
            raise serializers.ValidationError(
                {
                    "crypto_amount": (
                        f"Minimum deposit for {symbol} is {asset['minimum_deposit_amount']}."
                    )
                }
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        symbol = validated_data["crypto_symbol"]
        asset = next(a for a in CRYPTO_ASSETS if a["symbol"] == symbol)
        return Transaction.objects.create(
            user=user,
            direction=Transaction.Direction.CREDIT,
            category=Transaction.Category.DEPOSIT,
            amount=Decimal("0"),
            currency_code=validated_data.get("currency_code", "USD"),
            status=Transaction.Status.PENDING,
            reference_code=self.context["reference_code"],
            description=f"Crypto deposit · {asset['name']}",
            counterparty_name=asset["network_name"],
            crypto_symbol=symbol,
            crypto_amount=validated_data["crypto_amount"],
            transaction_hash=validated_data.get("transaction_hash", ""),
            proof_image=validated_data.get("proof_image"),
        )


class LocalDepositCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0.01"))
    proof_image = serializers.ImageField(required=True)
    currency_code = serializers.CharField(required=False, max_length=3, default="USD")

    def validate_currency_code(self, value):
        from apps.wallets.currencies import CURRENCY_CODES

        if value not in CURRENCY_CODES:
            raise serializers.ValidationError("Unsupported currency code.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.enable_transfer:
            raise serializers.ValidationError(
                "Local bank deposits are not enabled for your account. Contact support or use crypto deposit."
            )
        if not user.bank_account_number or not user.bank_name:
            raise serializers.ValidationError(
                "Bank account details are not configured for your account. Please contact support."
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        bank_label = user.bank_name
        return Transaction.objects.create(
            user=user,
            direction=Transaction.Direction.CREDIT,
            category=Transaction.Category.DEPOSIT,
            amount=validated_data["amount"],
            currency_code=validated_data.get("currency_code", user.bank_currency or "USD"),
            status=Transaction.Status.PENDING,
            reference_code=self.context["reference_code"],
            description="Local bank deposit",
            counterparty_name=bank_label,
            proof_image=validated_data["proof_image"],
        )
