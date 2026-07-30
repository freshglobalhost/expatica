from project.base_settings import *  # noqa: F403

SECRET_KEY = "django-insecure-dev-only-change-in-production"
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "pennycredit.db",
    }
}

CORS_ALLOWED_ORIGINS = [
    "https://expaticaonline.com",
    "https://www.expaticaonline.com",
     "http://localhost:3000",
    "http://127.0.0.1:3000",
]

REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [  # noqa: F405
    "rest_framework.permissions.AllowAny",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


