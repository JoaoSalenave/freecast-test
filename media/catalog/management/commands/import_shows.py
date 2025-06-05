from django.core.management.base import BaseCommand
from catalog.tasks import import_shows_task

class Command(BaseCommand):
    help = "Run import_shows_task synchronously (no Celery)"

    def handle(self, *args, **kwargs):
        import_shows_task()
        self.stdout.write(self.style.SUCCESS("import_shows_task completed synchronously"))