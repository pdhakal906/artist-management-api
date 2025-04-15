from fastapi import APIRouter, HTTPException, Depends, Path, Query
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
)


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

    for row in rows:
        artists.append(
            ArtistOut(
                id=row["id"],
                user_id=row["user_id"],
                first_release_year=row["first_release_year"],
                no_of_albums_released=row["no_of_albums_released"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                # user fields (flat)
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


@router.get("/artist/page-data")
async def page_data():
    return {"message": "page data here"}


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
