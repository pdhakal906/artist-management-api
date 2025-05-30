from fastapi import APIRouter, Depends, HTTPException, Path
from auth.jwt import create_access_token, decode_access_token
from auth.utils import verify_password
from auth.schemas.token import Token
from auth.schemas.users import UserLogin
from auth.services.users import (
    get_user_by_email,
    get_all_users,
    get_users_count,
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
)
from auth.schemas.users import UserOut, UserSignup, PaginatedUserResponse, UserUpdate
from fastapi import Query
from passlib.context import CryptContext
from middlewares.user_check import is_superadmin, is_manager, is_artist

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


@router.post("/signup")
async def signup(user: UserSignup):
    existing = await get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    try:
        user = await create_user(
            user.first_name,
            user.last_name,
            user.email,
            hashed_password,
            user.role,
            user.phone,
            user.dob,
            user.gender,
            user.address,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"user": dict(user)}


@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    user = await get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token(
        data={"id": user["id"], "sub": user["email"], "role": user["role"]}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/users",
    response_model=PaginatedUserResponse,
)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    userInfo: dict = Depends(decode_access_token),
):
    if not is_superadmin(userInfo):
        raise HTTPException(
            status_code=403, detail="You are not allowed to access this resource"
        )

    rows = await get_all_users(page, page_size)
    total_users = await get_users_count()
    total_pages = (total_users + page_size - 1) // page_size

    users = []
    for row in rows:
        users.append(
            UserOut(
                id=row[0],
                first_name=row[1],
                last_name=row[2],
                email=row[3],
                role=row[4],
                phone=row[5],
                dob=str(row[6]),
                gender=row[7],
                address=row[8],
                created_at=str(row[9]),
                updated_at=str(row[10]),
            )
        )
    return PaginatedUserResponse(
        page=page,
        page_size=page_size,
        total_users=total_users,
        total_pages=total_pages,
        users=users,
    )


@router.get("/users/page-data")
async def get_page_data():
    user_roles = ["super_admin", "artist_manager", "artist"]

    return {"roles": user_roles}


@router.get(
    "/users/{user_id}",
    response_model=UserOut,
)
async def get_user(
    user_id: int = Path(..., ge=1),
    userInfo: dict = Depends(decode_access_token),
):
    if not is_superadmin(userInfo):
        raise HTTPException(
            status_code=403, detail="You are not allowed to access this resource"
        )

    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = dict(user)

    user["created_at"] = str(user["created_at"])
    user["updated_at"] = str(user["updated_at"])

    return UserOut(**user)


@router.put("/users/{user_id}", response_model=UserOut)
async def update(user_id: int = Path(..., ge=1), user: UserUpdate = ...):

    existing_user = await get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user.model_dump(exclude_unset=True)
    updated_data = await update_user(user_id, UserUpdate(**update_data))
    updated_data["dob"] = str(updated_data["dob"])
    updated_data["created_at"] = str(updated_data["created_at"])
    updated_data["updated_at"] = str(updated_data["updated_at"])
    return updated_data


@router.delete("/users/{user_id}", status_code=204)
async def delete(
    user_id: int = Path(..., ge=1),
    userInfo: dict = Depends(decode_access_token),
):
    if not is_superadmin(userInfo):
        raise HTTPException(
            status_code=403, detail="You are not allowed to access this resource"
        )

    existing_user = await get_user_by_id(user_id)
    existing_user = dict(existing_user)
    if existing_user.get("role") == "super_admin":
        raise HTTPException(status_code=403, detail="Cannot delete super admin user")
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    await delete_user(user_id)
