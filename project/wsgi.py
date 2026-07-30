import os

from django.core.wsgi import get_wsgi_application

try:
    from pathlib import Path
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.development_settings")

application = get_wsgi_application()
