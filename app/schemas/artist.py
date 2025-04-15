from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List


class ArtistBase(BaseModel):
    user_id: int
    first_release_year: int
    no_of_albums_released: int


class ArtistOut(ArtistBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # User fields (flattened)
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    dob: datetime
    gender: str  # or Literal["male", "female", "other"]
    address: str
    role: str  # or Literal["super_admin", "artist_manager", "artist"]
    user_created_at: datetime
    user_updated_at: datetime


class ArtistCreate(ArtistBase):
    pass


class ArtistUpdate(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    phone: str
    dob: datetime
    gender: str  # or Literal["male", "female", "other"]
    address: str


class PaginatedArtistResponse(BaseModel):
    page: int
    page_size: int
    total_artist: int
    total_pages: int
    artists: List[ArtistOut]
