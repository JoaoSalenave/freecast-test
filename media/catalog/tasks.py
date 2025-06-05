from celery_app import app
from celery import shared_task
from catalog.models import Show, Season, Episode, Movie, Source
import requests
from datetime import datetime, date
import random

@shared_task
def import_shows_task():
    """
    1. Fetch the shows.json feed.
    2. For each show:
       - Create or update the Show object.
       - Create two Seasons (Season 1 and Season 2).
       - In each Season, create two Episodes (Episode 1 and Episode 2).
       - For each Episode, create one dummy Source.
       - Set kinopoisk_rating to 0.0 (placeholder).
    """
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
            release_date = (
                datetime.strptime(first_aired, "%Y-%m-%d").date()
                if first_aired
                else None
            )
        except ValueError:
            release_date = None

        imdb_rating = item.get("imdb_rating") or 0.0
        kinopoisk_rating = 0.0 

        show_obj, _ = Show.objects.update_or_create(
            title=title,
            defaults={
                "description": description,
                "image": image,
                "release_date": release_date,
                "imdb_rating": imdb_rating,
                "kinopoisk_rating": kinopoisk_rating,
            },
        )

        for season_number in [1, 2]:
            season_obj, _ = Season.objects.get_or_create(
                show=show_obj,
                number=season_number,
                defaults={"description": f"Placeholder season {season_number}"},
            )

            for ep_number in [1, 2]:
                ep_title = f"Episode {ep_number} (Placeholder)"
                episode_date = release_date or date.today()
                episode_obj, _ = Episode.objects.get_or_create(
                    season=season_obj,
                    number=ep_number,
                    defaults={
                        "title": ep_title,
                        "description": "",
                        "release_date": episode_date,
                    },
                )

                Source.objects.get_or_create(
                    episode=episode_obj,
                    url="https://example.com/episode-placeholder.mp4",
                    source_type="direct",
                )


@shared_task
def import_movies_task():
    """
    1. Fetch the movies.json feed.
    2. For each movie:
       - Create or update the Movie object.
       - Add one dummy Source.
    """
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
        imdb_rating = item.get("imdb_rating") or 0.0
        kinopoisk_rating = 0.0

        movie_obj, _ = Movie.objects.update_or_create(
            title=title,
            defaults={
                "description": description,
                "image": image,
                "release_date": release_date,
                "imdb_rating": imdb_rating,
                "kinopoisk_rating": kinopoisk_rating,
                "release_year": year,
            },
        )

        Source.objects.get_or_create(
            movie=movie_obj,
            url="https://example.com/movie-placeholder.mp4",
            source_type="direct",
        )


@shared_task
def update_ratings_task():
    """
    In prod/actual project: 
      - Query OMDb/TMDb for IMDb rating (using an API key).
      - Scrape Kinopoisk, or related.
    Here: placeholder sets all ratings to random value between 5.0 and 9.0.
    """
    for m in Movie.objects.all():
        ## TODO: replace this with a real API call fetch kinopoisk_rating.
        m.kinopoisk_rating = round(random.uniform(5.0, 9.0), 1)
        m.save()
    for s in Show.objects.all():
        ## TODO: same as above
        s.kinopoisk_rating = round(random.uniform(5.0, 9.0), 1)
        s.save()


@shared_task
def validate_sources_task():
    """
    In prod/actual project:
      - Use a HEAD (or GET) request to each Source.url.
      - If non-200, set is_active=False, optionally store a 'last_checked' timestamp.
    Here: placeholder will mark any non-200 or exception as inactive.
    """
    for src in Source.objects.all():
        try:
            r = requests.head(src.url, timeout=2)
            if r.status_code != 200:
                # TODO: maybe log the reason, or retry with exponential backoff.
                src.is_active = False
                src.save()
        except Exception:
            src.is_active = False
            src.save()
