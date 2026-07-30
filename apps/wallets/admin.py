from django.contrib import admin

from .models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "currency_code",
        "balance",
        "btc_balance",
        "eth_balance",
        "usdt_balance",
        "sol_balance",
        "bnb_balance",
        "ltc_balance",
    )
    list_filter = ("currency_code",)
