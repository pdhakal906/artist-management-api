from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    dob: datetime
    role: str
    phone: str
    gender: str
    address: str


class UserOut(UserBase):
    id: int
    created_at: str
    updated_at: str


class UserSignup(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    dob: datetime
    phone: str
    gender: str
    address: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserInfo(BaseModel):
    id: int
    sub: str
    role: str
    exp: int


class PaginatedUserResponse(BaseModel):
    page: int
    page_size: int
    total_users: int
    total_pages: int
    users: List[UserOut]
