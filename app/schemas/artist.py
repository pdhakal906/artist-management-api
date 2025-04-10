from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List


class ArtistBase(BaseModel):
    name: str
    dob: datetime
    gender: str
    address: str
    first_release_year: int
    no_of_albums_released: int


class ArtistOut(ArtistBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ArtistCreate(ArtistBase):
    pass


class ArtistUpdate(ArtistBase):
    pass


class PaginatedArtistResponse(BaseModel):
    page: int
    page_size: int
    total_artist: int
    total_pages: int
    artists: List[ArtistOut]
