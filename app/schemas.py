from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Literal


# ---------- Advertisement ----------

class AdvertisementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    author: str = Field(..., min_length=1, max_length=100)


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    author: Optional[str] = Field(None, min_length=1, max_length=100)


class AdvertisementResponse(AdvertisementBase):
    id: int
    author_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- User ----------

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    group: Literal['user', 'admin'] = 'user'


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    group: Optional[Literal['user', 'admin']] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Auth ----------

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    expires_in: int  # секунды