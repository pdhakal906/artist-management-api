from fastapi import APIRouter, HTTPException
from schemas.users import UserSignup
from services.users import create_user, get_user_by_email
from passlib.context import CryptContext

# initialize router
ROUTE_PREFIX = "/users"
router = APIRouter(prefix=ROUTE_PREFIX)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/signup")
async def signup(user: UserSignup):
    existing = await get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    await create_user(user.username, user.email, hashed_password)
    return {"message": "User created successfully"}
