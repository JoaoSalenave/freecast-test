from django.core.management.base import BaseCommand
import celery_app
from catalog.tasks import validate_sources_task
from celery.exceptions import CeleryError

class Command(BaseCommand):
    help = "Run validate_sources_task (via Celery if possible; otherwise run synchronously)"

    def handle(self, *args, **kwargs):
        try:
            validate_sources_task.delay()
            self.stdout.write(self.style.SUCCESS("validate_sources_task enqueued to Celery"))
        except (CeleryError, ConnectionError) as e:
            self.stdout.write(self.style.WARNING(
                "WARNING: could not enqueue task. "
                "Broker down? Running validate_sources_task synchronously…"
            ))
            validate_sources_task()
            self.stdout.write(self.style.SUCCESS("validate_sources_task completed synchronously"))