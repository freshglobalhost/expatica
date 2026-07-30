from rest_framework import serializers

from apps.wallets.currencies import CURRENCY_CODES

from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            "id",
            "currency_code",
            "balance",
            "btc_balance",
            "eth_balance",
            "usdt_balance",
            "sol_balance",
            "bnb_balance",
            "ltc_balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "balance",
            "btc_balance",
            "eth_balance",
            "usdt_balance",
            "sol_balance",
            "bnb_balance",
            "ltc_balance",
            "created_at",
            "updated_at",
        ]

    def validate_currency_code(self, value):
        if value not in CURRENCY_CODES:
            raise serializers.ValidationError("Unsupported currency code.")
        return value
