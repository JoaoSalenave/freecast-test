from django.core.management.base import BaseCommand
import celery_app 
from catalog.tasks import update_ratings_task
from celery.exceptions import CeleryError

class Command(BaseCommand):
    help = "Run update_ratings_task (via Celery if possible; otherwise run synchronously)"

    def handle(self, *args, **kwargs):
        try:
            update_ratings_task.delay()
            self.stdout.write(self.style.SUCCESS("update_ratings_task enqueued to Celery"))
        except (CeleryError, ConnectionError) as e:
            self.stdout.write(self.style.WARNING(
                "WARNING: could not enqueue task. "
                "Broker down? Running update_ratings_task synchronously…"
            ))
            update_ratings_task()
            self.stdout.write(self.style.SUCCESS("update_ratings_task completed synchronously"))