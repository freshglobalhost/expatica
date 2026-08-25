from django.contrib import admin

from .models import Transfer, TransferMethod


@admin.register(TransferMethod)
class TransferMethodAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "category", "is_active", "display_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "user", "kind", "method", "amount", "status", "created_at")
    list_filter = ("kind", "status", "method")
    search_fields = ("reference_code", "user__email", "user__username")
