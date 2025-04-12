from fastapi import APIRouter, HTTPException, Depends, Path, Query
from auth.jwt import decode_access_token
from schemas.music import (
    MusicCreate,
    MusicOut,
    MusicUpdate,
    PaginatedMusicResponse,
)
from middlewares.user_check import is_superadmin, is_manager, is_artist
from services.music import (
    create_music,
    get_music_by_id,
    get_music_by_artist_id,
    get_music_count,
    get_all_music,
    update_music,
    delete_music,
)


router = APIRouter()


@router.post("/music", response_model=MusicOut)
async def create(music: MusicCreate):
    music = await create_music(music)
    return dict(music)


@router.get("/music", response_model=PaginatedMusicResponse)
async def list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
):
    rows = await get_all_music(page, page_size)
    total_music = await get_music_count()
    total_pages = (total_music + page_size - 1) // page_size
    music = []
    for row in rows:
        music.append(
            MusicOut(
                id=row[0],
                artist_id=row[1],
                title=str(row[2]),
                album_name=row[3],
                genre=row[4],
                created_at=str(row[5]),
                updated_at=str(row[6]),
            )
        )
    return PaginatedMusicResponse(
        page=page,
        page_size=page_size,
        total_music=total_music,
        total_pages=total_pages,
        music=music,
    )


@router.get("/music/page-data")
async def page_data():
    return {"genre": ["rnb", "country", "classic", "rock", "jazz"]}


@router.put("/music/{music_id}", response_model=MusicOut)
async def update(music_id: int = Path(..., ge=1), music: MusicUpdate = ...):
    existing_music = await get_music_by_id(music_id)
    if not existing_music:
        raise HTTPException(status_code=404, detail="Music not found")

    updated_music = await update_music(music_id, music)
    updated_music["created_at"] = str(updated_music["created_at"])
    updated_music["updated_at"] = str(updated_music["updated_at"])

    return updated_music


@router.delete("/music/{music_id}", status_code=204)
async def delete(
    music_id: int = Path(..., ge=1),
    userInfo: dict = Depends(decode_access_token),
):
    if not is_superadmin(userInfo):
        raise HTTPException(
            status_code=403, detail="You are not allowed to access this resource"
        )
    existing_music = await get_music_by_id(music_id)
    if not existing_music:
        raise HTTPException(status_code=404, detail="Music not found")
    await delete_music(music_id)
