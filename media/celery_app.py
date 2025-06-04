import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'media'))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

from celery import Celery

app = Celery("media")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
