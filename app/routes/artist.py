from fastapi import APIRouter, Depends, HTTPException, Path, Query
from passlib.context import CryptContext
from fastapi.security import APIKeyHeader
from fastapi.security import OAuth2PasswordBearer

from auth.jwt import create_access_token, decode_access_token
from auth.utils import verify_password
from auth.schemas.token import Token
from schemas.artist import (
    ArtistCreate,
    ArtistBase,
    ArtistOut,
    ArtistUpdate,
    PaginatedArtistResponse,
)
from middlewares.user_check import is_superadmin, is_manager, is_artist

header_scheme = APIKeyHeader(name="Authorization", auto_error=False)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


@router.post("/artist")
async def create(artist: ArtistCreate, token: str = Depends(header_scheme)):
    print(artist.name)
    return {"message": "Artist created successfully"}


@router.get(
    "/artist",
    response_model=PaginatedArtistResponse,
)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    token: str = Depends(header_scheme),
):
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    userInfo = decode_access_token(token)

    if not userInfo:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not is_superadmin(userInfo):
        raise HTTPException(
            status_code=403, detail="You are not allowed to access this resource"
        )

    return PaginatedArtistResponse(
        page=page,
        page_size=page_size,
        total_artist=None,
        total_pages=None,
        users=None,
    )


@router.get("/artist/page-data")
async def get_page_data():

    return {"message": "page data here"}


@router.put("/artist/{artist_id}", response_model=ArtistOut)
async def update(artist_id: int = Path(..., ge=1), artist: ArtistUpdate = ...):

    return {"message": "Artist updated successfully"}


@router.delete("/artist/{user_id}", status_code=204)
async def delete(user_id: int = Path(..., ge=1), token: str = Depends(header_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    userInfo = decode_access_token(token)

    if not userInfo:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not is_superadmin(userInfo):
        raise HTTPException(
            status_code=403, detail="You are not allowed to access this resource"
        )
