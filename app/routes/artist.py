from fastapi import APIRouter, HTTPException, Depends, Path, Query, File, UploadFile
import csv, os
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime
from auth.jwt import decode_access_token
from schemas.artist import (
    ArtistCreate,
    ArtistOut,
    ArtistUpdate,
    PaginatedArtistResponse,
)
from middlewares.user_check import is_superadmin, is_manager, is_artist
from services.artist import (
    create_artist,
    get_artist_by_id,
    get_artists_count,
    get_all_artist,
    update_artist,
    delete_artist,
    get_all_artists_without_pagination,
)
from utils.bulk_create_artists_from_csv import bulk_create_artists_from_csv
from pathlib import Path as OsPath


router = APIRouter()


@router.post("/artist", response_model=ArtistOut)
async def create(artist: ArtistCreate):
    artist = await create_artist(artist)
    return dict(artist)


@router.get("/artist", response_model=PaginatedArtistResponse)
async def list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
):
    rows = await get_all_artist(page, page_size)
    total_artist = await get_artists_count()
    total_pages = (total_artist + page_size - 1) // page_size
    artists = []
    if rows:
        for row in rows:
            artists.append(
                ArtistOut(
                    id=row["id"],
                    user_id=row["user_id"],
                    first_release_year=row["first_release_year"],
                    no_of_albums_released=row["no_of_albums_released"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    email=row["email"],
                    phone=row["phone"],
                    dob=row["dob"],
                    gender=row["gender"],
                    address=row["address"],
                    role=row["role"],
                    user_created_at=row["user_created_at"],
                    user_updated_at=row["user_updated_at"],
                )
            )

    return PaginatedArtistResponse(
        page=page,
        page_size=page_size,
        total_artist=total_artist,
        total_pages=total_pages,
        artists=artists,
    )


@router.get(
    "/artist/{artist_id}",
    response_model=ArtistOut,
)
async def get_artist(
    artist_id: int = Path(..., ge=1),
    userInfo: dict = Depends(decode_access_token),
):
    if not is_superadmin(userInfo) and not is_manager(userInfo):
        raise HTTPException(
            status_code=403, detail="You are not allowed to access this resource"
        )
    artist = await get_artist_by_id(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    artist = dict(artist)
    artist["created_at"] = str(artist["created_at"])
    artist["updated_at"] = str(artist["updated_at"])
    return ArtistOut(**artist)


@router.put("/artist/{artist_id}", response_model=ArtistOut)
async def update(artist_id: int = Path(..., ge=1), artist: ArtistUpdate = ...):
    existing_artist = await get_artist_by_id(artist_id)
    if not existing_artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    updated_artist = await update_artist(artist_id, artist)
    updated_artist["created_at"] = str(updated_artist["created_at"])
    updated_artist["updated_at"] = str(updated_artist["updated_at"])

    return updated_artist


@router.delete("/artist/{artist_id}", status_code=204)
async def delete(
    artist_id: int = Path(..., ge=1),
    userInfo: dict = Depends(decode_access_token),
):
    if not is_superadmin(userInfo) and not is_manager(userInfo):
        raise HTTPException(
            status_code=403, detail="You are not allowed to access this resource"
        )
    existing_artist = await get_artist_by_id(artist_id)
    if not existing_artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    await delete_artist(artist_id)


@router.post("/artist/upload-csv", response_model=List[ArtistOut])
async def create_artists_from_csv(
    file: UploadFile = File(...),
    userInfo: dict = Depends(decode_access_token),
):
    if not is_superadmin(userInfo) and not is_manager(userInfo):
        raise HTTPException(
            status_code=403, detail="You are not allowed to access this resource"
        )
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        artists = await bulk_create_artists_from_csv(file)
        flattened_artists = []
        for artist in artists:
            flattened_artists.append(
                {
                    "id": artist["id"],
                    "user_id": artist["user_id"],
                    "first_release_year": artist["first_release_year"],
                    "no_of_albums_released": artist["no_of_albums_released"],
                    "created_at": artist["created_at"],
                    "updated_at": artist["updated_at"],
                    "first_name": artist["user"]["first_name"],
                    "last_name": artist["user"]["last_name"],
                    "email": artist["user"]["email"],
                    "phone": artist["user"]["phone"],
                    "dob": artist["user"]["dob"],
                    "gender": artist["user"]["gender"],
                    "address": artist["user"]["address"],
                    "role": artist["user"]["role"],
                    "user_created_at": artist["user_created_at"],
                    "user_updated_at": artist["user_updated_at"],
                }
            )

        return flattened_artists

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artists/download")
async def download_artists():

    artists = await get_all_artists_without_pagination()

    if not artists:
        return JSONResponse({"detail": "No artists found"}, status_code=404)

    static_dir = OsPath("static_files")

    filename = f"artists_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = static_dir / filename

    artist_dicts = [dict(row) for row in artists]
    headers = artist_dicts[0].keys()

    with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(artist_dicts)

    return JSONResponse({"url": f"/static/{filename}"})
