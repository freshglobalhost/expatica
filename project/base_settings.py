from pathlib import Path
from project.settings.packages.rest_framework_settings import *
from project.utils.settings import get_env_variable
BASE_DIR = Path(__file__).resolve().parent.parent

SITE_NAME = "PennyCredit"

SECRET_KEY = "change-me-in-production"
DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = True

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_resized",
    "apps.core",
    "apps.accounts",
    "apps.wallets",
    "apps.transactions",
    "apps.banking",
    "apps.loans",
    "apps.cards",
    "apps.investments",
    "apps.savings",
    "apps.support",
    'cloudinary_storage',
    'cloudinary',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]



DATABASES = {}  # configure your DB in production

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/assets/"

STATICFILES_DIRS = [
    BASE_DIR / "project/assets",
]
STATIC_ROOT = BASE_DIR / "assets"

MEDIA_URL = "/uploads/"

MEDIA_ROOT = get_env_variable(
    "MEDIA_ROOT", BASE_DIR / "project/uploads")


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


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


