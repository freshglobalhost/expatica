from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class HelpCategory(BaseModel):
    slug = models.SlugField(unique=True, max_length=64)
    name = models.CharField(max_length=128)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name_plural = "help categories"


class HelpArticle(BaseModel):
    category = models.ForeignKey(HelpCategory, on_delete=models.CASCADE, related_name="articles")
    slug = models.SlugField(max_length=128)
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_published = models.BooleanField(default=True)

    class Meta:
        unique_together = [("category", "slug")]
        ordering = ["title"]


class FAQ(BaseModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.ForeignKey(
        HelpCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faqs",
    )
    display_order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"


class SupportTicket(BaseModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_tickets",
    )
    reference_code = models.CharField(max_length=32, unique=True, db_index=True)
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)

    class Meta:
        ordering = ["-created_at"]


class TicketMessage(BaseModel):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message_body = models.TextField()
    is_staff_reply = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
