from django.contrib import admin

from .models import CardRequest, CardTransaction, VirtualCard


@admin.register(VirtualCard)
class VirtualCardAdmin(admin.ModelAdmin):
    list_display = ("card_name", "user", "network", "last_four_digits", "balance", "is_frozen")
    list_filter = ("network", "is_frozen")


@admin.register(CardRequest)
class CardRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "card_name", "issuance_fee", "status", "created_at")


@admin.register(CardTransaction)
class CardTransactionAdmin(admin.ModelAdmin):
    list_display = ("card", "merchant_name", "amount", "created_at")
