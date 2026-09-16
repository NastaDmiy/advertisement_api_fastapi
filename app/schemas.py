from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class AdvertisementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    author: str = Field(..., min_length=1, max_length=100)


class AdvertisementCreate(AdvertisementBase):
    """Схема для POST — все поля обязательны"""
    pass


class AdvertisementUpdate(BaseModel):
    """Схема для PATCH — все поля опциональны"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    author: Optional[str] = Field(None, min_length=1, max_length=100)


class AdvertisementResponse(AdvertisementBase):
    """Схема ответа"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)