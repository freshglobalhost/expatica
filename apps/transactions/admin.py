from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference_code",
        "user",
        "category",
        "direction",
        "amount",
        "currency_code",
        "crypto_symbol",
        "crypto_amount",
        "status",
        "created_at",
    )
    list_filter = ("category", "status", "crypto_symbol", "currency_code")
    search_fields = ("reference_code", "user__email", "transaction_hash")
