from fastapi import APIRouter, HTTPException
from typing import List
from catalog.models import Movie, Source
from service.schemas.movie import Movie as MovieSchema, MovieSource as MovieSourceSchema

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=List[MovieSchema])
def get_movies():
    output: List[MovieSchema] = []
    for movie in Movie.objects.all():
        sources_data = [
            MovieSourceSchema(
                id=src.id,
                url=src.url,
                source_type=src.source_type,
            )
            for src in movie.sources.all()
        ]
        output.append(
            MovieSchema(
                id=movie.id,
                title=movie.title,
                description=movie.description,
                image=movie.image,
                release_date=movie.release_date,
                imdb_rating=movie.imdb_rating,
                kinopoisk_rating=movie.kinopoisk_rating,
                sources=sources_data,
            )
        )
    return output


@router.get("/{movie_id}", response_model=MovieSchema)
def get_movie(movie_id: int):
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        raise HTTPException(status_code=404, detail="Movie not found")

    sources_data = [
        MovieSourceSchema(
            id=src.id,
            url=src.url,
            source_type=src.source_type,
        )
        for src in movie.sources.all()
    ]

    return MovieSchema(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        image=movie.image,
        release_date=movie.release_date,
        imdb_rating=movie.imdb_rating,
        kinopoisk_rating=movie.kinopoisk_rating,
        sources=sources_data,
    )


@router.get("/{movie_id}/sources", response_model=List[MovieSourceSchema])
def get_movie_sources(movie_id: int):
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        raise HTTPException(status_code=404, detail="Movie not found")

    return [
        MovieSourceSchema(
            id=src.id,
            url=src.url,
            source_type=src.source_type,
        )
        for src in movie.sources.all()
    ]
