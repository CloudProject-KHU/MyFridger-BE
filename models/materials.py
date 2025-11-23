from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime


class MaterialBase(SQLModel):
    name: str
    image_url: Optional[str] = None
    price: int
    currency: str = "KRW"
    category: str
    purchased_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    expired_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    quantity: int
    quantity_unit: Optional[str] = None


class Material(MaterialBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(SQLModel):
    name: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[int] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    purchased_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    quantity: Optional[int] = None
    quantity_unit: Optional[str] = None


class MaterialResponse(MaterialBase):
    id: int
