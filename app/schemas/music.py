from pydantic import BaseModel
from datetime import datetime
from typing import List


class MusicBase(BaseModel):
    artist_id: int
    title: str
    album_name: str
    genre: str


class MusicOut(MusicBase):
    id: int
    created_at: datetime
    updated_at: datetime


class MusicCreate(MusicBase):
    pass


class MusicUpdate(MusicBase):
    pass


class PaginatedMusicResponse(BaseModel):
    page: int
    page_size: int
    total_music: int
    total_pages: int
    music: List[MusicOut]
