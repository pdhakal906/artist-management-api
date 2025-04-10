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
                id=row[0],
                name=row[1],
                dob=str(row[2]),
                gender=row[3],
                address=row[4],
                first_release_year=row[5],
                no_of_albums_released=row[6],
                created_at=str(row[7]),
                updated_at=str(row[8]),
            )
        )
    return PaginatedArtistResponse(
        page=page,
        page_size=page_size,
        total_artist=total_artist,
        total_pages=total_pages,
        artists=artists,
    )


@router.get("/artist/page-data")
async def page_data():
    return {"message": "page data here"}


@router.put("/artist/{artist_id}", response_model=ArtistOut)
async def update(artist_id: int = Path(..., ge=1), artist: ArtistUpdate = ...):

    return {"message": "Artist updated successfully"}


@router.delete("/artist/{user_id}", status_code=204)
async def delete(user_id: int = Path(..., ge=1)):
    pass

    # if not userInfo:
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    # if not is_superadmin(userInfo):
    #     raise HTTPException(
    #         status_code=403, detail="You are not allowed to access this resource"
    #     )
