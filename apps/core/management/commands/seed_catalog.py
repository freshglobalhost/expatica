from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.banking.models import TransferMethod
from apps.loans.models import LoanProduct


LOAN_PRODUCTS = [
    {
        "slug": "personal",
        "name": "Personal Loan",
        "description": "Flexible financing for personal expenses, debt consolidation, and major purchases.",
        "minimum_amount": Decimal("1000"),
        "maximum_amount": Decimal("50000"),
        "minimum_interest_rate": Decimal("5.99"),
        "available_terms_months": [12, 24, 36, 48, 60],
    },
    {
        "slug": "business",
        "name": "Business Loan",
        "description": "Capital for equipment, inventory, expansion, and working capital needs.",
        "minimum_amount": Decimal("5000"),
        "maximum_amount": Decimal("250000"),
        "minimum_interest_rate": Decimal("6.49"),
        "available_terms_months": [12, 24, 36, 48, 60, 72],
    },
    {
        "slug": "home",
        "name": "Home Loan",
        "description": "Mortgage and property financing with competitive rates.",
        "minimum_amount": Decimal("25000"),
        "maximum_amount": Decimal("500000"),
        "minimum_interest_rate": Decimal("4.25"),
        "available_terms_months": [120, 180, 240, 360],
    },
    {
        "slug": "auto",
        "name": "Auto Loan",
        "description": "New and used vehicle financing with fast approval.",
        "minimum_amount": Decimal("5000"),
        "maximum_amount": Decimal("75000"),
        "minimum_interest_rate": Decimal("4.99"),
        "available_terms_months": [24, 36, 48, 60, 72],
    },
]

TRANSFER_METHODS = [
    ("wire", "Wire Transfer", "international", 1),
    ("local", "Local Transfer", "domestic", 2),
    ("paypal", "PayPal", "digital", 3),
    ("skrill", "Skrill", "digital", 4),
    ("googlepay", "Google Pay", "digital", 5),
    ("western", "Western Union", "cash", 6),
    ("wise", "Wise", "international", 7),
    ("payoneer", "Payoneer", "business", 8),
]


class Command(BaseCommand):
    help = "Seed loan products and transfer methods for the dashboard."

    def handle(self, *args, **options):
        for item in LOAN_PRODUCTS:
            LoanProduct.objects.update_or_create(
                slug=item["slug"],
                defaults={**item, "is_active": True},
            )
        self.stdout.write(self.style.SUCCESS(f"Loan products: {len(LOAN_PRODUCTS)}"))

        for slug, name, category, order in TRANSFER_METHODS:
            TransferMethod.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": category,
                    "display_order": order,
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Transfer methods: {len(TRANSFER_METHODS)}"))
