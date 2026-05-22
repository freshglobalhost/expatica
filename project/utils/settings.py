import os

from django.core.exceptions import ImproperlyConfigured


def get_env_variable(var_name, default=None):
    """Return environment variable or default; raise if missing and no default."""
    value = os.getenv(var_name)
    if value is not None:
        return value
    if default is not None:
        return default
    raise ImproperlyConfigured(f"Set the {var_name} environment variable")


def get_app_settings():
    return os.getenv("DJANGO_SETTINGS_MODULE", "project.production_settings")
