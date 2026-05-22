from project.base_settings import *  # noqa: F403

SECRET_KEY = "django-insecure-dev-only-change-in-production"
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]

DATABASES["default"] = {  # noqa: F405
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "pennycreditonline.db",  # noqa: F405
}

CORS_ALLOWED_ORIGINS = [
    "https://pennycreditonline.com",
    "https://www.pennycreditonline.com",
     "http://localhost:3000",
    "http://127.0.0.1:3000",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [  # noqa: F405
    "rest_framework.permissions.AllowAny",
]
