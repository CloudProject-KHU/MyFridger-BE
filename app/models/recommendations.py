from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, ForeignKey


class RecommendationBase(SQLModel):
    recipe_id: int = Field(foreign_key="recipe.id")
    # user_id: Optional[int] = None  # 사용자 ID (인증 구현 시 사용)


class Recommendation(RecommendationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    liked: Optional[bool]


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationResponse(SQLModel):
    id: int
    recipe_id: int
    name: str
    thumbnail_url: str


class RecommendationListResponse(SQLModel):
    result: list[RecommendationResponse]


# AI 기반 소비기한 추정 Request/Response
class ExpirationEstimateRequest(SQLModel):
    name: str
    category: str
    purchased_at: datetime


class ExpirationEstimateResponse(SQLModel):
    estimated_expiration_date: datetime
    confidence: float  # 0~1 범위
    notes: str
