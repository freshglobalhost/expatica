from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.wallets.models import Wallet

from .models import Gender

User = get_user_model()


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
            "address",
            "gender",
            "gender_label",
            "profile_picture",
            "profile_picture_url",
            "kyc_status",
            "has_transaction_pin",
            "is_kyc_verified",
            "is_profile_complete",
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
            "profile_picture_url",
        ]

    def get_profile_picture_url(self, obj):
        return obj.get_profile_picture_url(self.context.get("request"))


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "country",
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


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    transaction_pin = serializers.CharField(write_only=True, min_length=4, max_length=4)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "country",
            "address",
            "gender",
            "transaction_pin",
        ]

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_transaction_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Transaction PIN must be 4 digits.")
        return value

    def create(self, validated_data):
        pin = validated_data.pop("transaction_pin")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.set_transaction_pin(pin)
        user.save()
        Wallet.objects.create(user=user, currency_code="USD", balance=0)
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
