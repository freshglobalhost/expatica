from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        from django.conf import settings
        from django.contrib import admin

        site_name = getattr(settings, "SITE_NAME", "PennyCredit")
        admin.site.site_header = f"{site_name} Administration"
        admin.site.site_title = site_name
        admin.site.index_title = "Dashboard"
