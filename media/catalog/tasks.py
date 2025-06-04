from celery import shared_task
from catalog.models import Show, Season, Episode, Movie, Source
import requests
from datetime import datetime, date

@shared_task
def import_shows_task():
    url = "https://channelsapi.s3.amazonaws.com/media/test/shows.json"
    response = requests.get(url)
    data = response.json()

    for item in data:
        title = item.get("name")
        description = item.get("description", "")
        raw_image = item.get("image", "")
        image = raw_image if raw_image.startswith("http") else f"https:{raw_image}"
        first_aired = item.get("first_aired")
        try:
            release_date = datetime.strptime(first_aired, "%Y-%m-%d").date() if first_aired else None
        except ValueError:
            release_date = None
        imdb = item.get("imdb_rating") or 0.0
        kinopoisk = 0.0

        show_obj, _ = Show.objects.update_or_create(
            title=title,
            defaults={
                "description": description,
                "image": image,
                "release_date": release_date,
                "imdb_rating": imdb,
                "kinopoisk_rating": kinopoisk,
            },
        )

        season_obj, _ = Season.objects.get_or_create(
            show=show_obj,
            number=1,
            defaults={"description": "Placeholder season"},
        )
        episode_obj, _ = Episode.objects.get_or_create(
            season=season_obj,
            number=1,
            defaults={
                "title": "Episode 1 (Placeholder)",
                "description": "",
                "release_date": release_date or date.today(),
            },
        )

        Source.objects.get_or_create(
            episode=episode_obj,
            url="https://example.com/episode-placeholder.mp4",
            source_type="direct",
        )


@shared_task
def import_movies_task():
    url = "https://channelsapi.s3.amazonaws.com/media/test/movies.json"
    response = requests.get(url)
    data = response.json()

    for item in data:
        title = item.get("name")
        description = item.get("description", "")
        raw_image = item.get("image", "")
        image = raw_image if raw_image.startswith("http") else f"https:{raw_image}"
        year = item.get("release_year")
        release_date = date(year, 1, 1) if year else None
        imdb = item.get("imdb_rating") or 0.0
        kinopoisk = 0.0

        movie_obj, _ = Movie.objects.update_or_create(
            title=title,
            defaults={
                "description": description,
                "image": image,
                "release_date": release_date,
                "imdb_rating": imdb,
                "kinopoisk_rating": kinopoisk,
                "release_year": year,
            },
        )

        Source.objects.get_or_create(
            movie=movie_obj,
            url="https://example.com/movie-placeholder.mp4",
            source_type="direct",
        )
