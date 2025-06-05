from django.core.management.base import BaseCommand
from catalog.tasks import update_ratings_task

class Command(BaseCommand):
    help = "Run update_ratings_task synchronously (no Celery)"

    def handle(self, *args, **kwargs):
        update_ratings_task()
        self.stdout.write(self.style.SUCCESS("update_ratings_task completed synchronously"))