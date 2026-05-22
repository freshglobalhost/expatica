from django.contrib import admin, messages

from apps.core.utils import generate_reference_code

from .models import Transaction
from .services import WALLET_CATEGORIES, prepare_admin_transaction


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

    def save_model(self, request, obj, form, change):
        if not change:
            if not obj.reference_code:
                obj.reference_code = generate_reference_code("TX")
            error = prepare_admin_transaction(obj)
            if error:
                messages.error(request, error)
                return
        super().save_model(request, obj, form, change)
        if not change and obj.category in WALLET_CATEGORIES:
            messages.success(
                request,
                f"Transaction {obj.reference_code} completed; wallet updated and user notified by email.",
            )
