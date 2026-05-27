from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class LoanProduct(BaseModel):
    slug = models.SlugField(unique=True, max_length=32)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    minimum_amount = models.DecimalField(max_digits=14, decimal_places=2)
    maximum_amount = models.DecimalField(max_digits=14, decimal_places=2)
    minimum_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    available_terms_months = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class LoanApplication(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loan_applications",
    )
    product = models.ForeignKey(LoanProduct, on_delete=models.PROTECT, related_name="applications")
    reference_code = models.CharField(max_length=32, unique=True, db_index=True)
    requested_amount = models.DecimalField(max_digits=14, decimal_places=2)
    term_months = models.PositiveIntegerField()
    purpose = models.TextField()
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    address = models.TextField(blank=True)
    employer = models.CharField(max_length=128, blank=True)
    job_title = models.CharField(max_length=128, blank=True)
    annual_income = models.CharField(max_length=32, blank=True)
    employment_years = models.CharField(max_length=16, blank=True)
    id_document = models.FileField(upload_to="loan_applications/id/", blank=True)
    income_document = models.FileField(upload_to="loan_applications/income/", blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            old_status = (
                LoanApplication.objects.filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )
        super().save(*args, **kwargs)
        if old_status != self.status:
            from .notifications import send_loan_application_status_email
            from .services import create_loan_from_approved_application

            disbursement_info = None
            if self.status == self.Status.APPROVED:
                _, disbursement_info = create_loan_from_approved_application(self)

            send_loan_application_status_email(
                self,
                old_status=old_status,
                disbursement_info=disbursement_info,
            )


class Loan(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        CLOSED = "closed", "Closed"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans",
    )
    application = models.OneToOneField(
        LoanApplication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loan",
    )
    product = models.ForeignKey(LoanProduct, on_delete=models.PROTECT, related_name="loans")
    reference_code = models.CharField(max_length=32, unique=True, db_index=True)
    principal_amount = models.DecimalField(max_digits=14, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    applied_on = models.DateField()
    disbursed_on = models.DateField(null=True, blank=True)
    outstanding_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            old_status = (
                Loan.objects.filter(pk=self.pk).values_list("status", flat=True).first()
            )
        super().save(*args, **kwargs)
        if old_status != self.status:
            from .notifications import send_loan_status_email
            from .services import disburse_loan_principal

            disbursement_info = None
            if self.status == self.Status.APPROVED:
                disbursement_info = disburse_loan_principal(self)

            send_loan_status_email(
                self,
                old_status=old_status,
                disbursement_info=disbursement_info,
            )


class LoanRepayment(BaseModel):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="repayments")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    due_on = models.DateField()
    paid_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["due_on"]
