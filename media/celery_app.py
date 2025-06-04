import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

sys.path.insert(0, str(BASE_DIR))

from celery import Celery

app = Celery("media")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
