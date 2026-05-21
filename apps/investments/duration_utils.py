import re
from datetime import timedelta

from django.utils import timezone


def parse_duration_label(label: str) -> timedelta:
    text = (label or "").strip().lower()
    if not text:
        return timedelta(days=30)

    patterns = [
        (r"(\d+)\s*days?", lambda n: timedelta(days=n)),
        (r"(\d+)\s*weeks?", lambda n: timedelta(weeks=n)),
        (r"(\d+)\s*months?", lambda n: timedelta(days=n * 30)),
        (r"(\d+)\s*years?", lambda n: timedelta(days=n * 365)),
    ]
    for pattern, builder in patterns:
        match = re.search(pattern, text)
        if match:
            return builder(int(match.group(1)))
    return timedelta(days=30)


def maturity_datetime(duration_label: str):
    return timezone.now() + parse_duration_label(duration_label)
