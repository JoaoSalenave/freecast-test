import os
import sys
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

sys.path.insert(0, str(BASE_DIR))

from celery import Celery
from celery.schedules import crontab

app = Celery("media")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):

    sender.send_task("catalog.tasks.import_movies_task")
    sender.send_task("catalog.tasks.import_shows_task")

    sender.add_periodic_task(
        timedelta(hours=24),
        sender.signature("catalog.tasks.import_movies_task"),
        name="import-movies-every-24h",
    )
    
    sender.add_periodic_task(
        timedelta(hours=24),
        sender.signature("catalog.tasks.import_shows_task"),
        name="import-shows-every-24h",
    )

    sender.add_periodic_task(
        crontab(minute="*/3"),
        sender.signature("catalog.tasks.update_ratings_task"),
        name="update-ratings-every-3-mins",
    )

    sender.add_periodic_task(
        crontab(minute=0, hour="*/6"),
        sender.signature("catalog.tasks.validate_sources_task"),
        name="validate-sources-every-6h",
    )