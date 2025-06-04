from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class MovieSource(BaseModel):
    id: int
    url: str
    source_type: str

    class Config:
        from_attributes = True

class Movie(BaseModel):
    id: int
    title: str
    description: str
    image: str
    release_date: Optional[date]  
    imdb_rating: float
    kinopoisk_rating: float
    sources: List[MovieSource] = []  

    class Config:
        from_attributes = True
