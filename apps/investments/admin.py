from django.contrib import admin

from .models import InvestmentPlan, UserInvestment


@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "minimum_amount", "maximum_amount", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(UserInvestment)
class UserInvestmentAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "user", "plan", "invested_amount", "status", "matures_at")
    list_filter = ("status",)
