# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth.jwt import create_access_token
from auth.utils import verify_password
from auth.schemas.token import Token
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


@router.post("/signup")
async def signup(user: UserSignup):
    existing = await get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    await create_user(
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
    return {"message": "User created successfully"}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token(
        data={"id": user["id"], "sub": user["email"], "role": user["role"]}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/users", response_model=PaginatedUserResponse)
async def list_users(page: int = Query(1, ge=1), page_size: int = Query(10, le=100)):
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


@router.put("/users/{user_id}", response_model=UserOut)
async def update(user_id: int = Path(..., ge=1), user: UserUpdate = ...):

    existing_user = await get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user.model_dump(exclude_unset=True)

    hashed_password = pwd_context.hash(update_data["password"])
    update_data["password"] = hashed_password
    update_data["dob"] = update_data["dob"].replace(tzinfo=None)
    updated_data = await update_user(user_id, UserUpdate(**update_data))
    updated_data["dob"] = str(updated_data["dob"])
    updated_data["created_at"] = str(updated_data["created_at"])
    updated_data["updated_at"] = str(updated_data["updated_at"])
    return updated_data


@router.delete("/users/{user_id}", status_code=204)
async def delete(user_id: int = Path(..., ge=1)):

    existing_user = await get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    await delete_user(user_id)
