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


class ArtistCreate(ArtistBase):
    pass


class ArtistOut(ArtistBase):
    id: int
    created_at: str
    updated_at: str


class PaginatedArtistResponse(BaseModel):
    page: int
    page_size: int
    total_artist: int
    total_pages: int
    users: List[ArtistOut]
