from django.core.management.base import BaseCommand
from catalog.tasks import import_movies_task

class Command(BaseCommand):
    help = "Run import_movies_task synchronously (no Celery)"

    def handle(self, *args, **kwargs):
        import_movies_task()
        self.stdout.write(self.style.SUCCESS("import_movies_task completed synchronously"))