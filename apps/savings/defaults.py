from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction

from .models import AutoSaveRule, LockedSavingsAccount

User = get_user_model()

DEFAULT_AUTO_SAVE_RULES = [
    {
        "rule_name": "Round-ups",
        "description": "Round up card purchases to the nearest $1",
        "is_enabled": True,
        "total_saved_amount": Decimal("124.00"),
        "rule_settings": {"type": "round_up", "increment": 1},
    },
    {
        "rule_name": "Payday save",
        "description": "Save 10% of incoming deposits automatically",
        "is_enabled": True,
        "total_saved_amount": Decimal("850.00"),
        "rule_settings": {"type": "percent_deposit", "percent": 10},
    },
    {
        "rule_name": "Weekly transfer",
        "description": "Transfer $50 every Monday to savings",
        "is_enabled": False,
        "total_saved_amount": Decimal("0.00"),
        "rule_settings": {"type": "scheduled", "amount": 50, "frequency": "weekly", "day": "monday"},
    },
]

DEFAULT_LOCKED_ACCOUNTS = [
    {
        "account_name": "12-Month Fixed",
        "locked_amount": Decimal("15000.00"),
        "interest_rate_label": "5.2% APY",
        "unlocks_on": None,
    },
    {
        "account_name": "6-Month Boost",
        "locked_amount": Decimal("5000.00"),
        "interest_rate_label": "4.8% APY",
        "unlocks_on": None,
    },
]


def _unlock_date(months: int) -> date:
    today = date.today()
    month_index = today.month - 1 + months
    year = today.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, min(today.day, 28))


def ensure_default_auto_save_rules(user) -> int:
    if AutoSaveRule.objects.filter(user=user).exists():
        return 0
    with transaction.atomic():
        if AutoSaveRule.objects.filter(user=user).exists():
            return 0
        AutoSaveRule.objects.bulk_create(
            [AutoSaveRule(user=user, **item) for item in DEFAULT_AUTO_SAVE_RULES]
        )
    return len(DEFAULT_AUTO_SAVE_RULES)


def ensure_default_locked_savings(user) -> int:
    if LockedSavingsAccount.objects.filter(user=user).exists():
        return 0
    offsets = [12, 6]
    with transaction.atomic():
        if LockedSavingsAccount.objects.filter(user=user).exists():
            return 0
        LockedSavingsAccount.objects.bulk_create(
            [
                LockedSavingsAccount(user=user, **{**item, "unlocks_on": _unlock_date(months)})
                for item, months in zip(DEFAULT_LOCKED_ACCOUNTS, offsets)
            ]
        )
    return len(DEFAULT_LOCKED_ACCOUNTS)


def ensure_default_savings_for_user(user) -> None:
    ensure_default_auto_save_rules(user)
    ensure_default_locked_savings(user)


def ensure_default_savings_for_all_users() -> tuple[int, int]:
    rules_created = 0
    locked_created = 0
    for user in User.objects.all():
        rules_created += ensure_default_auto_save_rules(user)
        locked_created += ensure_default_locked_savings(user)
    return rules_created, locked_created
