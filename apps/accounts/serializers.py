from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from PIL import UnidentifiedImageError
from rest_framework import serializers

from apps.wallets.models import Wallet

from .models import Gender
from .utils import process_profile_picture

User = get_user_model()


class AssignedBankAccountSerializer(serializers.Serializer):
    account_holder = serializers.CharField()
    bank_name = serializers.CharField()
    account_number = serializers.CharField()
    routing_or_swift = serializers.CharField(allow_blank=True)
    country = serializers.CharField(allow_blank=True)
    currency = serializers.CharField()
    instructions = serializers.CharField(allow_blank=True)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    initials = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    account_reference = serializers.CharField(read_only=True)
    gender_label = serializers.CharField(read_only=True, allow_null=True)
    has_transaction_pin = serializers.BooleanField(read_only=True)
    is_kyc_verified = serializers.BooleanField(read_only=True)
    is_profile_complete = serializers.BooleanField(read_only=True)
    profile_picture_url = serializers.SerializerMethodField()
    enable_transfer = serializers.BooleanField(read_only=True)
    assigned_bank_account = serializers.SerializerMethodField()
    referral_code = serializers.SerializerMethodField()
    referral_link = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "initials",
            "display_name",
            "account_reference",
            "phone",
            "country",
            "currency_code",
            "address",
            "gender",
            "gender_label",
            "profile_picture",
            "profile_picture_url",
            "kyc_status",
            "has_transaction_pin",
            "is_kyc_verified",
            "is_profile_complete",
            "enable_transfer",
            "assigned_bank_account",
            "referral_code",
            "referral_link",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "email",
            "username",
            "kyc_status",
            "date_joined",
            "full_name",
            "initials",
            "display_name",
            "account_reference",
            "gender_label",
            "has_transaction_pin",
            "is_kyc_verified",
            "is_profile_complete",
            "enable_transfer",
            "assigned_bank_account",
            "referral_code",
            "referral_link",
            "currency_code",
            "profile_picture_url",
        ]

    def get_profile_picture_url(self, obj):
        return obj.get_profile_picture_url(self.context.get("request"))

    def get_assigned_bank_account(self, obj):
        if not obj.enable_transfer:
            return None
        if not obj.bank_account_number or not obj.bank_name:
            return None
        return {
            "account_holder": obj.bank_account_holder or obj.full_name,
            "bank_name": obj.bank_name,
            "account_number": obj.bank_account_number,
            "routing_or_swift": obj.bank_routing_or_swift or "",
            "country": obj.bank_country or obj.country or "",
            "currency": obj.bank_currency or obj.currency_code or "USD",
            "instructions": obj.bank_deposit_instructions or "",
        }

    def get_referral_code(self, obj):
        from .referral import referral_code_for

        return referral_code_for(obj)

    def get_referral_link(self, obj):
        from .referral import referral_link_for

        return referral_link_for(obj)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "country",
            "currency_code",
            "address",
            "gender",
            "profile_picture",
        ]

    def validate_gender(self, value):
        if value in (None, ""):
            return None
        valid = {choice[0] for choice in Gender.choices}
        if value not in valid:
            raise serializers.ValidationError("Invalid gender value.")
        return value

    def validate_profile_picture(self, value):
        if value in (None, "", False):
            return None
        max_bytes = 5 * 1024 * 1024
        if getattr(value, "size", 0) > max_bytes:
            raise serializers.ValidationError("Profile picture must be 5 MB or smaller.")
        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif",
            "image/jpg",
        }
        content_type = (getattr(value, "content_type", None) or "").lower()
        if content_type and content_type not in allowed_types:
            raise serializers.ValidationError(
                "Unsupported image type. Use JPEG, PNG, WebP, or GIF."
            )
        try:
            return process_profile_picture(value)
        except UnidentifiedImageError as exc:
            raise serializers.ValidationError("Invalid image file.") from exc
        except Exception as exc:
            raise serializers.ValidationError(f"Could not process image: {exc}") from exc


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    transaction_pin = serializers.CharField(write_only=True, min_length=4, max_length=4)
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "country",
            "currency_code",
            "address",
            "gender",
            "transaction_pin",
            "referral_code",
        ]

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_transaction_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Transaction PIN must be 4 digits.")
        return value

    def create(self, validated_data):
        from .referral import allocate_unique_username

        pin = validated_data.pop("transaction_pin")
        password = validated_data.pop("password")
        validated_data.pop("referral_code", None)
        username = allocate_unique_username(
            validated_data.get("first_name") or "",
            validated_data.get("last_name") or "",
            validated_data.get("email") or "",
        )
        user = User(**validated_data, username=username)
        user.set_password(password)
        user.set_transaction_pin(pin)
        user.save()
        currency = user.currency_code or "USD"
        Wallet.objects.create(user=user, currency_code=currency, balance=0)
        from apps.savings.defaults import ensure_default_savings_for_user

        ensure_default_savings_for_user(user)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value, self.context["request"].user)
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class TransactionPinChangeSerializer(serializers.Serializer):
    current_transaction_pin = serializers.CharField(
        min_length=4,
        max_length=4,
        write_only=True,
        required=False,
        allow_blank=True,
    )
    new_transaction_pin = serializers.CharField(min_length=4, max_length=4, write_only=True)

    def validate_new_transaction_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Transaction PIN must be 4 digits.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        current = attrs.get("current_transaction_pin") or ""
        if user.transaction_pin:
            if not current or not user.check_transaction_pin(current):
                raise serializers.ValidationError(
                    {"current_transaction_pin": "Current transaction PIN is incorrect."}
                )
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_transaction_pin(self.validated_data["new_transaction_pin"])
        user.save(update_fields=["transaction_pin"])
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Code must be 6 digits.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class VerifyTransactionPinSerializer(serializers.Serializer):
    transaction_pin = serializers.CharField(min_length=4, max_length=4, write_only=True)

    def validate_transaction_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Transaction PIN must be 4 digits.")
        user = self.context["request"].user
        if not user.transaction_pin:
            raise serializers.ValidationError("Transaction PIN is not set on this account.")
        if not user.check_transaction_pin(value):
            raise serializers.ValidationError("Incorrect transaction PIN.")
        return value
