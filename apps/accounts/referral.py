import re
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import get_user_model


def slugify_handle(value: str) -> str:
    value = (value or "").strip().lower()
    value = value.split("@", 1)[0]
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value[:30] or ""


def allocate_unique_username(first_name: str, last_name: str, email: str) -> str:
    User = get_user_model()
    base = slugify_handle(f"{first_name}{last_name}") or slugify_handle(email) or "user"
    candidate = base
    suffix = 1
    while User.objects.filter(username__iexact=candidate).exists():
        suffix += 1
        extra = str(suffix)
        candidate = f"{base[: 150 - len(extra)]}{extra}"
    return candidate


def referral_code_for(user) -> str:
    username = (getattr(user, "username", None) or "").strip()
    if username and "@" not in username:
        return username
    handle = slugify_handle(getattr(user, "email", "") or username)
    if handle:
        return handle
    if user.pk:
        return f"user{user.pk}"
    return username


def referral_link_for(user) -> str:
    base = getattr(settings, "FRONTEND_URL", "https://expaticaonline.com").rstrip("/")
    return f"{base}/signup?ref={quote(referral_code_for(user))}"


def find_referrer(code: str):
    User = get_user_model()
    code = (code or "").strip()
    if not code:
        return None

    user = User.objects.filter(username__iexact=code).first()
    if user:
        return user

    handle = slugify_handle(code)
    if not handle:
        return None

    user = User.objects.filter(username__iexact=handle).first()
    if user:
        return user

    for candidate in User.objects.filter(email__istartswith=f"{handle}@"):
        if slugify_handle(candidate.email) == handle:
            return candidate
    return None
