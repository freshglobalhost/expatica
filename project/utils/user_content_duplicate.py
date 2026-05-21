"""
Same-calendar-day duplicate guard for user-submitted text (forum posts, blog comments, Q&A).

Goal: each piece of content a user posts in a day must be distinct from their other posts
that day (normalized comparison), including across different threads or blog posts.
"""
import datetime
import re

from django.utils import timezone
from django.utils.html import strip_tags

# Ignore only trivial repeats (e.g. "ok", "thanks"); still blocks short copy-paste spam.
DUPLICATE_USER_TEXT_MIN_LEN = 1


def normalized_user_text(text):
    """Lowercase, strip HTML, strip punctuation/symbols, collapse whitespace — for comparing user-submitted text."""
    if not text:
        return ""
    t = strip_tags(str(text))
    # Strip all non-alphanumeric characters (keeps letters, numbers, and whitespace)
    t = re.sub(r'[^a-zA-Z0-9\s]', '', t)
    t = " ".join(t.split())
    return t.strip().lower()


def local_day_bounds():
    """Start/end datetimes for the user's current calendar day (project timezone)."""
    today = timezone.localdate()
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min), tz)
    end = start + datetime.timedelta(days=1)
    return start, end
