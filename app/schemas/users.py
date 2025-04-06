from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserSignup(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    created_at: str
