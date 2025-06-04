from fastapi import APIRouter, HTTPException
from typing import List
from catalog.models import Show, Season, Episode, Source
from service.schemas.show import (
    Show as ShowSchema,
    Season as SeasonSchema,
    Episode as EpisodeSchema,
    EpisodeSource as EpisodeSourceSchema,
)

router = APIRouter(prefix="/shows", tags=["shows"])


@router.get("/", response_model=List[ShowSchema])
def get_shows():
    output: List[ShowSchema] = []

    for show in Show.objects.all():
        seasons_data: List[SeasonSchema] = []
        for season in show.seasons.all().order_by("number"):
            episodes_data: List[EpisodeSchema] = []
            for ep in season.episodes.all().order_by("number"):
                sources_data = [
                    EpisodeSourceSchema(
                        id=src.id,
                        url=src.url,
                        source_type=src.source_type,
                    )
                    for src in ep.sources.all()
                ]
                episodes_data.append(
                    EpisodeSchema(
                        id=ep.id,
                        number=ep.number,
                        title=ep.title,
                        release_date=ep.release_date,
                        sources=sources_data,
                    )
                )
            seasons_data.append(
                SeasonSchema(
                    id=season.id,
                    number=season.number,
                    episodes=episodes_data,
                )
            )

        output.append(
            ShowSchema(
                id=show.id,
                title=show.title,
                description=show.description,
                image=show.image,
                release_date=show.release_date,
                imdb_rating=show.imdb_rating,
                kinopoisk_rating=show.kinopoisk_rating,
                seasons=seasons_data,
            )
        )

    return output


@router.get("/{show_id}", response_model=ShowSchema)
def get_show(show_id: int):
    try:
        show = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        raise HTTPException(status_code=404, detail="Show not found")

    seasons_data: List[SeasonSchema] = []
    for season in show.seasons.all().order_by("number"):
        episodes_data: List[EpisodeSchema] = []
        for ep in season.episodes.all().order_by("number"):
            sources_data = [
                EpisodeSourceSchema(
                    id=src.id,
                    url=src.url,
                    source_type=src.source_type,
                )
                for src in ep.sources.all()
            ]
            episodes_data.append(
                EpisodeSchema(
                    id=ep.id,
                    number=ep.number,
                    title=ep.title,
                    release_date=ep.release_date,
                    sources=sources_data,
                )
            )

        seasons_data.append(
            SeasonSchema(
                id=season.id,
                number=season.number,
                episodes=episodes_data,
            )
        )

    return ShowSchema(
        id=show.id,
        title=show.title,
        description=show.description,
        image=show.image,
        release_date=show.release_date,
        imdb_rating=show.imdb_rating,
        kinopoisk_rating=show.kinopoisk_rating,
        seasons=seasons_data,
    )


@router.get("/{show_id}/seasons", response_model=List[SeasonSchema])
def get_show_seasons(show_id: int):
    try:
        show = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        raise HTTPException(status_code=404, detail="Show not found")

    output: List[SeasonSchema] = []
    for season in show.seasons.all().order_by("number"):
        episodes_data: List[EpisodeSchema] = []
        for ep in season.episodes.all().order_by("number"):
            sources_data = [
                EpisodeSourceSchema(
                    id=src.id,
                    url=src.url,
                    source_type=src.source_type,
                )
                for src in ep.sources.all()
            ]
            episodes_data.append(
                EpisodeSchema(
                    id=ep.id,
                    number=ep.number,
                    title=ep.title,
                    release_date=ep.release_date,
                    sources=sources_data,
                )
            )
        output.append(
            SeasonSchema(
                id=season.id,
                number=season.number,
                episodes=episodes_data,
            )
        )
    return output


@router.get("/{show_id}/episodes", response_model=List[EpisodeSchema])
def get_show_episodes(show_id: int):
    try:
        show = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        raise HTTPException(status_code=404, detail="Show not found")

    output: List[EpisodeSchema] = []
    for season in show.seasons.all().order_by("number"):
        for ep in season.episodes.all().order_by("number"):
            sources_data = [
                EpisodeSourceSchema(
                    id=src.id,
                    url=src.url,
                    source_type=src.source_type,
                )
                for src in ep.sources.all()
            ]
            output.append(
                EpisodeSchema(
                    id=ep.id,
                    number=ep.number,
                    title=ep.title,
                    release_date=ep.release_date,
                    sources=sources_data,
                )
            )
    return output


@router.get("/episodes/{episode_id}/sources", response_model=List[EpisodeSourceSchema])
def get_episode_sources(episode_id: int):
    try:
        ep = Episode.objects.get(id=episode_id)
    except Episode.DoesNotExist:
        raise HTTPException(status_code=404, detail="Episode not found")

    return [
        EpisodeSourceSchema(
            id=src.id,
            url=src.url,
            source_type=src.source_type,
        )
        for src in ep.sources.all()
    ]
