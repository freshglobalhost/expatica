from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.hashers import is_password_usable, make_password

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "country",
        "currency_code",
        "enable_transfer",
        "kyc_status",
        "is_active",
    )
    list_filter = ("kyc_status", "currency_code", "enable_transfer", "is_staff", "is_active", "country")
    search_fields = ("email", "username", "first_name", "last_name", "phone")
    ordering = ("-date_joined",)
    filter_horizontal = ()

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "username", "referred_by")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Profile",
            {
                "fields": (
                    "phone",
                    "country",
                    "currency_code",
                    "address",
                    "gender",
                    "profile_picture",
                    "kyc_status",
                    "transaction_pin",
                ),
            },
        ),
        (
            "Local bank deposit",
            {
                "fields": (
                    "enable_transfer",
                    "bank_account_holder",
                    "bank_name",
                    "bank_account_number",
                    "bank_routing_or_swift",
                    "bank_country",
                    "bank_currency",
                    "bank_deposit_instructions",
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "first_name", "last_name"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        pin = form.cleaned_data.get("transaction_pin") if form.is_valid() else None
        if pin and (not change or "transaction_pin" in form.changed_data):
            if len(pin) == 4 and pin.isdigit() and not is_password_usable(pin):
                obj.transaction_pin = make_password(pin)
        super().save_model(request, obj, form, change)
        if change and "currency_code" in form.changed_data:
            from apps.wallets.services import sync_user_wallet_currency

            sync_user_wallet_currency(obj)
