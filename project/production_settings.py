import os
import dj_database_url
from project.base_settings import *
from project.settings.packages.celery_settings import *
from project.settings.local.email_settings import *
SECRET_KEY = get_env_variable("SECRET_KEY")
DEBUG = int(get_env_variable("DEBUG", "0"))
INSTALLED_APPS.append("storages")
DATABASES["default"] = dj_database_url.parse(get_env_variable("DATABASE_URL"), conn_max_age=600)
ALLOWED_HOSTS = ["api.expaticaonline.com", "expaticaonline.com", "www.expaticaonline.com","expaticaonline.vercel.app","expaticaonline-b851a5f25fef.herokuapp.com"]

REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [
    "rest_framework.permissions.AllowAny",
]

CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)


CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)


CORS_ALLOWED_ORIGINS = [
    "https://expaticaonline.com",
    "https://www.expaticaonline.com",
    "expaticaonline.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
