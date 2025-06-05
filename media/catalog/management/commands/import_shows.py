from django.core.management.base import BaseCommand
import celery_app 
from catalog.tasks import import_shows_task
from celery.exceptions import CeleryError

class Command(BaseCommand):
    help = "Run import_shows_task (via Celery if possible; otherwise run synchronously)"

    def handle(self, *args, **kwargs):
        try:
            import_shows_task.delay()
            self.stdout.write(self.style.SUCCESS("import_shows_task enqueued to Celery"))
        except (CeleryError, ConnectionError) as e:
            self.stdout.write(self.style.WARNING(
                "WARNING: could not enqueue task. "
                "Broker down? Running import_shows_task synchronously…"
            ))
            import_shows_task()
            self.stdout.write(self.style.SUCCESS("import_shows_task completed synchronously"))