from fastapi import APIRouter, HTTPException
from typing import List
from catalog.models import Movie
from service.schemas.movie import Movie as MovieSchema, MovieSource as MovieSourceSchema

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("/", response_model=List[MovieSchema])
def get_movies():
    return list(Movie.objects.all())


@router.get("/{movie_id}", response_model=MovieSchema)
def get_movie(movie_id: int):
    try:
        return Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        raise HTTPException(status_code=404, detail="Movie not found")


@router.get("/{movie_id}/sources", response_model=List[MovieSourceSchema])
def get_movie_sources(movie_id: int):
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        raise HTTPException(status_code=404, detail="Movie not found")

    return list(movie.sources.all())
