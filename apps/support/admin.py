from django.contrib import admin

from .models import FAQ, HelpArticle, HelpCategory, SupportTicket, TicketMessage


class HelpArticleInline(admin.TabularInline):
    model = HelpArticle
    extra = 0
    fields = ("title", "slug", "is_published")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [HelpArticleInline]
    ordering = ("display_order",)


@admin.register(HelpArticle)
class HelpArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "slug", "is_published", "created_at")
    list_filter = ("category", "is_published")
    search_fields = ("title", "body", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "display_order", "is_published")
    list_filter = ("category", "is_published")
    search_fields = ("question", "answer")
    ordering = ("display_order",)


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "user", "subject", "status", "priority", "created_at")
    list_filter = ("status", "priority")
    inlines = [TicketMessageInline]
