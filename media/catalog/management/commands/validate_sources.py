from django.core.management.base import BaseCommand
from catalog.tasks import validate_sources_task

class Command(BaseCommand):
    help = "Run validate_sources_task synchronously (no Celery)"

    def handle(self, *args, **kwargs):
        validate_sources_task()
        self.stdout.write(self.style.SUCCESS("validate_sources_task completed synchronously"))