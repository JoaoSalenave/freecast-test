from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class EpisodeSource(BaseModel):
    id: int
    url: str
    source_type: str

    class Config:
        from_attributes = True

class Episode(BaseModel):
    id: int
    number: int
    title: str
    release_date: Optional[date]  
    sources: List[EpisodeSource] = []

    class Config:
        from_attributes = True

class Season(BaseModel):
    id: int
    number: int
    episodes: List[Episode] = []

    class Config:
        from_attributes = True

class Show(BaseModel):
    id: int
    title: str
    description: str
    image: str
    release_date: Optional[date] 
    imdb_rating: float
    kinopoisk_rating: float
    seasons: List[Season] = []     

    class Config:
        from_attributes = True
