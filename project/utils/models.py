import auto_prefetch
from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils.text import slugify
from tinymce.models import HTMLField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext as _


class VisibleManager(models.Manager):
    def get_queryset(self):
        """filters queryset to return only visible items"""
        return super().get_queryset().filter(visible=True)


class TimeBasedModel(auto_prefetch.Model):
    visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    objects = models.Manager()
    items = VisibleManager()


class NotificationModel(TimeBasedModel):
    message = models.CharField(max_length=500)
    sender = auto_prefetch.ForeignKey(
        "home.CustomUser", on_delete=models.SET_NULL, null=True, related_name="sender"
    )
    read = models.BooleanField(default=False)
    recipient = auto_prefetch.ForeignKey(
        "home.CustomUser", null=True, on_delete=models.CASCADE, related_name="recipient"
    )

    class Meta:
        ordering = ["-updated_at"]
        abstract = True

    def __str__(self):
        return truncatechars(self.message, 60)


class NamedTimeBasedModel(TimeBasedModel):
    name = models.CharField(max_length=200)

    class Meta:
        abstract = True
        ordering = ["name", "created_at"]

    def __str__(self):
        return self.name

    def title(self):
        """alias for `name` field"""
        return self.name


class CategoryModel(TimeBasedModel):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(null=True, blank=True, max_length=250)

    class Meta:
        verbose_name_plural = "categories"
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class BaseReview(TimeBasedModel):
    owner = auto_prefetch.ForeignKey(
        'home.CustomUser', on_delete=models.CASCADE, verbose_name=_("member")
    )
    text = HTMLField(max_length=150, verbose_name=_('text'))
    rating = models.PositiveSmallIntegerField(
        verbose_name=_("rating"),
        default=1,
        validators=[MaxValueValidator(5), MinValueValidator(1)],
    )

    def __str__(self):
        return f"{self.owner} - {self.rating}"

    @property
    def ratings(self):
        "return the ratings"
        return "❤" * self.rating

    class Meta(auto_prefetch.Model.Meta):
        abstract = True
        ordering = ["-created_at"]
