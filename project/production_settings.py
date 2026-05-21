import os
import dj_database_url
from project.base_settings import *  # noqa: F403
from project.settings.packages.celery_settings import *  # noqa: F403
from project.settings.local.email_settings import *  # noqa: F403
from project.utils.settings import get_env_variable

SECRET_KEY = get_env_variable("SECRET_KEY")
DEBUG = int(get_env_variable("DEBUG", "0"))
INSTALLED_APPS.append("storages")
DATABASES["default"] = dj_database_url.parse(get_env_variable("DATABASE_URL"), conn_max_age=600)

ALLOWED_HOSTS = [
    host.strip()
    for host in get_env_variable(
        "DJANGO_ALLOWED_HOSTS",
        "api.pennycreditonline.com,pennycreditonline.com,www.pennycreditonline.com",
    ).split(",")
    if host.strip()
]

# Frontend on Vercel — allow your production domain(s)
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in get_env_variable(
        "CORS_ALLOWED_ORIGINS",
        "https://pennycreditonline.com,https://www.pennycreditonline.com",
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True


CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dl9r87apa',
    'API_KEY': '582245214259671',
    'API_SECRET': 'x1VIGv7Lsi4LEQ60oEwXBJbQnYg'
}

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}