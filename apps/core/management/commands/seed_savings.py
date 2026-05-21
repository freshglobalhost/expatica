from django.core.management.base import BaseCommand

from apps.savings.defaults import ensure_default_savings_for_all_users


class Command(BaseCommand):
    help = "Create default auto-save rules and locked savings for users who have none."

    def handle(self, *args, **options):
        rules, locked = ensure_default_savings_for_all_users()
        self.stdout.write(
            self.style.SUCCESS(
                f"Auto-save rules created: {rules}, locked accounts created: {locked}"
            )
        )
