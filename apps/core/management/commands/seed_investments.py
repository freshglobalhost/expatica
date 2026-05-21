from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.investments.models import InvestmentPlan


PLANS = [
    {
        "slug": "starter-savings",
        "name": "Starter Savings",
        "minimum_amount": Decimal("100"),
        "maximum_amount": Decimal("1000"),
        "return_type": "percent",
        "return_value": Decimal("5"),
        "duration_label": "7 Days",
        "returns_capital": True,
        "display_order": 1,
    },
    {
        "slug": "monthly-growth",
        "name": "Monthly Growth Plan",
        "minimum_amount": Decimal("500"),
        "maximum_amount": Decimal("5000"),
        "return_type": "percent",
        "return_value": Decimal("12"),
        "duration_label": "1 Months",
        "returns_capital": True,
        "display_order": 2,
    },
    {
        "slug": "premium-quarterly",
        "name": "Premium Quarterly",
        "minimum_amount": Decimal("3000"),
        "maximum_amount": Decimal("20000"),
        "return_type": "percent",
        "return_value": Decimal("25"),
        "duration_label": "3 Months",
        "returns_capital": True,
        "display_order": 3,
    },
    {
        "slug": "fixed-income-30",
        "name": "Fixed Income 30",
        "minimum_amount": Decimal("1000"),
        "maximum_amount": Decimal("10000"),
        "return_type": "fixed",
        "return_value": Decimal("150"),
        "duration_label": "30 Days",
        "returns_capital": True,
        "display_order": 4,
    },
    {
        "slug": "quick-returns",
        "name": "Quick Returns",
        "minimum_amount": Decimal("250"),
        "maximum_amount": Decimal("2500"),
        "return_type": "percent",
        "return_value": Decimal("8"),
        "duration_label": "2 Weeks",
        "returns_capital": True,
        "display_order": 5,
    },
    {
        "slug": "bi-annual-elite",
        "name": "Bi-Annual Elite",
        "minimum_amount": Decimal("7500"),
        "maximum_amount": Decimal("50000"),
        "return_type": "percent",
        "return_value": Decimal("45"),
        "duration_label": "6 Months",
        "returns_capital": True,
        "display_order": 6,
    },
    {
        "slug": "roi-only-60",
        "name": "ROI Only 60 Days",
        "minimum_amount": Decimal("2000"),
        "maximum_amount": Decimal("15000"),
        "return_type": "percent",
        "return_value": Decimal("18"),
        "duration_label": "60 Days",
        "returns_capital": False,
        "display_order": 7,
    },
    {
        "slug": "high-yield-annual",
        "name": "High Yield Annual",
        "minimum_amount": Decimal("15000"),
        "maximum_amount": Decimal("100000"),
        "return_type": "percent",
        "return_value": Decimal("75"),
        "duration_label": "12 Months",
        "returns_capital": True,
        "display_order": 8,
    },
    {
        "slug": "weekly-flex",
        "name": "Weekly Flex",
        "minimum_amount": Decimal("50"),
        "maximum_amount": Decimal("500"),
        "return_type": "percent",
        "return_value": Decimal("3"),
        "duration_label": "7 Days",
        "returns_capital": True,
        "display_order": 9,
    },
    {
        "slug": "diamond-vip",
        "name": "Diamond VIP",
        "minimum_amount": Decimal("50000"),
        "maximum_amount": Decimal("500000"),
        "return_type": "percent",
        "return_value": Decimal("120"),
        "duration_label": "12 Months",
        "returns_capital": True,
        "display_order": 10,
    },
]


class Command(BaseCommand):
    help = "Seed investment plans for the investments dashboard."

    def handle(self, *args, **options):
        for item in PLANS:
            InvestmentPlan.objects.update_or_create(
                slug=item["slug"],
                defaults={**item, "is_active": True},
            )
        self.stdout.write(self.style.SUCCESS(f"Investment plans: {len(PLANS)}"))
