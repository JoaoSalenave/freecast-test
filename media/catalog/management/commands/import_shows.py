from django.core.management.base import BaseCommand
from catalog.models import Show
import requests
from datetime import datetime

class Command(BaseCommand):
    help = 'Import shows from the JSON endpoint'

    def handle(self, *args, **kwargs):
        url = 'https://channelsapi.s3.amazonaws.com/media/test/shows.json'
        response = requests.get(url)
        data = response.json()
        
        for item in data:
            title = item.get('name')
            description = item.get('description', '')
            raw_image = item.get('image', '')
            image = raw_image if raw_image.startswith('http') else f'https:{raw_image}'
            first_aired = item.get('first_aired')
            try:
                release_date = datetime.strptime(first_aired, '%Y-%m-%d').date() if first_aired else None
            except ValueError:
                release_date = None
            imdb = item.get('imdb_rating') or 0.0
            kinopoisk = 0.0
            
            show_obj, created = Show.objects.update_or_create(
                title=title,
                defaults={
                    'description': description,
                    'image': image,
                    'release_date': release_date,
                    'imdb_rating': imdb,
                    'kinopoisk_rating': kinopoisk,
                }
            )
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Updated'}: {title}"))
