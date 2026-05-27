from django.contrib import admin, messages

from .models import Loan, LoanApplication, LoanProduct, LoanRepayment
from .services import create_loan_from_approved_application


@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "minimum_interest_rate", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.action(description="Approve selected applications and create loans")
def approve_and_disburse_loans(modeladmin, request, queryset):
    created = 0
    skipped = 0
    for application in queryset.select_related("product", "user"):
        if application.status == LoanApplication.Status.APPROVED and hasattr(application, "loan"):
            skipped += 1
            continue
        if application.status not in (
            LoanApplication.Status.PENDING,
            LoanApplication.Status.APPROVED,
        ):
            skipped += 1
            continue
        application.status = LoanApplication.Status.APPROVED
        application.save(update_fields=["status", "updated_at"])
        loan, _ = create_loan_from_approved_application(application)
        if loan:
            created += 1
    if created:
        modeladmin.message_user(
            request,
            f"Created {created} loan record(s) and repayment schedules.",
            messages.SUCCESS,
        )
    if skipped:
        modeladmin.message_user(
            request,
            f"Skipped {skipped} application(s) (already disbursed or invalid status).",
            messages.WARNING,
        )


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "user", "product", "requested_amount", "status", "created_at")
    list_filter = ("status",)
    actions = [approve_and_disburse_loans]
    readonly_fields = ("reference_code", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change and obj.pk:
            previous_status = (
                LoanApplication.objects.filter(pk=obj.pk).values_list("status", flat=True).first()
            )
        super().save_model(request, obj, form, change)
        became_approved = obj.status == LoanApplication.Status.APPROVED and (
            not change or previous_status != LoanApplication.Status.APPROVED
        )
        if became_approved and hasattr(obj, "loan") and obj.loan_id:
            messages.success(
                request,
                f"Loan {obj.loan.reference_code} created and disbursed to the user's wallet.",
            )


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "user", "product", "principal_amount", "status", "outstanding_balance")
    list_filter = ("status",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status == Loan.Status.APPROVED and obj.disbursed_on:
            messages.success(
                request,
                f"Loan {obj.reference_code} approved; funds disbursed to wallet.",
            )


@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):
    list_display = ("loan", "amount", "due_on", "paid_on")
