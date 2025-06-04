from django.core.management.base import BaseCommand
from catalog.models import Movie
import requests
from datetime import date

class Command(BaseCommand):
    help = 'Import movies from the JSON endpoint'

    def handle(self, *args, **kwargs):
        url = 'https://channelsapi.s3.amazonaws.com/media/test/movies.json'
        response = requests.get(url)
        data = response.json()
        for item in data:
            title = item.get('name')
            description = item.get('description', '')
            raw_image = item.get('image', '')
            image = raw_image if raw_image.startswith('http') else f'https:{raw_image}'
            year = item.get('release_year')
            release_date = date(year, 1, 1) if year else None
            imdb = item.get('imdb_rating') or 0.0
            kinopoisk = 0.0
            movie_obj, created = Movie.objects.update_or_create(
                title=title,
                defaults={
                    'description': description,
                    'image': image,
                    'release_date': release_date,
                    'imdb_rating': imdb,
                    'kinopoisk_rating': kinopoisk,
                    'release_year': year,
                }
            )
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Updated'}: {title}"))
