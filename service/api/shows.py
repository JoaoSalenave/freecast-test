from fastapi import APIRouter, HTTPException
from typing import List
from catalog.models import Show, Season, Episode
from service.schemas.show import Show as ShowSchema, Season as SeasonSchema, Episode as EpisodeSchema, EpisodeSource as EpisodeSourceSchema

router = APIRouter(prefix="/shows", tags=["shows"])

@router.get("/", response_model=List[ShowSchema])
def get_shows():
    return list(Show.objects.all())


@router.get("/{show_id}", response_model=ShowSchema)
def get_show(show_id: int):
    try:
        return Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        raise HTTPException(status_code=404, detail="Show not found")


@router.get("/{show_id}/seasons", response_model=List[SeasonSchema])
def get_show_seasons(show_id: int):
    try:
        show = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        raise HTTPException(status_code=404, detail="Show not found")

    return list(show.seasons.all())


@router.get("/{show_id}/episodes", response_model=List[EpisodeSchema])
def get_show_episodes(show_id: int):
    try:
        show = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        raise HTTPException(status_code=404, detail="Show not found")

    episodes = []
    for season in show.seasons.all().order_by("number"):
        episodes.extend(list(season.episodes.all().order_by("number")))
    return episodes


@router.get("/episodes/{episode_id}/sources", response_model=List[EpisodeSourceSchema])
def get_episode_sources(episode_id: int):
    try:
        ep = Episode.objects.get(id=episode_id)
    except Episode.DoesNotExist:
        raise HTTPException(status_code=404, detail="Episode not found")

    return list(ep.sources.all())
