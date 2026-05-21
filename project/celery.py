import os

from celery import Celery

from project.utils.settings import get_app_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", get_app_settings())

app = Celery("project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
