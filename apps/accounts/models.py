import secrets
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django_resized import ResizedImageField


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say", "Prefer not to say"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=64, blank=True)
    address = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, null=True, blank=True)
    profile_picture = ResizedImageField(
        size=[400, 400],
        quality=75,
        upload_to="documents/profile_pictures",
        null=True,
        blank=True,
        verbose_name="Profile picture",
    )
    transaction_pin = models.CharField(max_length=128, blank=True)
    kyc_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    enable_transfer = models.BooleanField(
        default=False,
        help_text="When enabled, the user can submit local bank deposit requests using assigned bank details.",
    )
    bank_account_holder = models.CharField(max_length=128, blank=True)
    bank_name = models.CharField(max_length=128, blank=True)
    bank_account_number = models.CharField(max_length=64, blank=True)
    bank_routing_or_swift = models.CharField(
        max_length=64,
        blank=True,
        help_text="Routing number, sort code, SWIFT/BIC, or IBAN as applicable.",
    )
    bank_country = models.CharField(max_length=64, blank=True)
    bank_currency = models.CharField(max_length=3, blank=True, default="USD")
    bank_deposit_instructions = models.TextField(blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    @property
    def initials(self) -> str:
        """Avatar fallback letters, e.g. SM for Sarah Mitchell."""
        first = (self.first_name or "").strip()
        last = (self.last_name or "").strip()
        if first and last:
            return f"{first[0]}{last[0]}".upper()
        if first:
            return first[:2].upper()
        if self.email:
            return self.email[:2].upper()
        return "?"

    @property
    def full_name(self) -> str:
        name = self.get_full_name().strip()
        return name if name else self.email

    @property
    def display_name(self) -> str:
        """Friendly label for UI headers (first name or email local-part)."""
        first = (self.first_name or "").strip()
        if first:
            return first
        if self.email and "@" in self.email:
            return self.email.split("@", 1)[0]
        return self.full_name

    @property
    def account_reference(self) -> str:
        """Stable public reference for support and profile screens."""
        return f"PC-{self.pk}" if self.pk else ""

    @property
    def gender_label(self) -> str | None:
        if not self.gender:
            return None
        return self.get_gender_display()

    @property
    def has_transaction_pin(self) -> bool:
        return bool(self.transaction_pin)

    def set_transaction_pin(self, raw_pin: str) -> None:
        self.transaction_pin = make_password(raw_pin)

    def check_transaction_pin(self, raw_pin: str) -> bool:
        if not self.transaction_pin:
            return False
        if check_password(raw_pin, self.transaction_pin):
            return True
        # Legacy rows: admin saved a plain 4-digit PIN instead of a hash
        if (
            len(self.transaction_pin) == 4
            and self.transaction_pin.isdigit()
            and self.transaction_pin == raw_pin
        ):
            self.set_transaction_pin(raw_pin)
            self.save(update_fields=["transaction_pin"])
            return True
        return False

    @property
    def is_kyc_verified(self) -> bool:
        return self.kyc_status == "verified"

    @property
    def is_profile_complete(self) -> bool:
        return bool(
            self.first_name
            and self.last_name
            and self.phone
            and self.country
        )

    def get_profile_picture_url(self, request=None) -> str | None:
        if not self.profile_picture:
            return None
        url = self.profile_picture.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class PasswordResetCode(models.Model):
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6)
    reset_token = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def create_for_email(cls, email: str):
        cls.objects.filter(email__iexact=email, is_used=False).update(is_used=True)
        code = f"{secrets.randbelow(1_000_000):06d}"
        reset_token = secrets.token_urlsafe(32)
        return cls.objects.create(
            email=email.lower(),
            code=code,
            reset_token=reset_token,
            expires_at=timezone.now() + timedelta(minutes=15),
        )

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
