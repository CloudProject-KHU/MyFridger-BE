from datetime import datetime
from typing import List, Optional
from enum import Enum
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ARRAY, String, DateTime


class Priority(str, Enum):
    """식재료 유통기한 우선순위"""
    HIGH = "HIGH"      # 3일 이내 만료
    MEDIUM = "MEDIUM"  # 7일 이내 만료
    NORMAL = "NORMAL"  # 여유 있음


class RecipeBase(SQLModel):
    recipe_id: Optional[int] = Field(default=None, primary_key=True)
    recipe_pat: str  # 국&찌개 (카테고리)
    method: str      # 조리 방법 (예: 찌기, 볶기 등)
    recipe_name: str
    thumbnail_url: str


class Recipe(RecipeBase, table=True):
    instructions: List[str] = Field(
        sa_column=Column(ARRAY(String)), default_factory=list
    )
    material_names: List[str] = Field(
        sa_column=Column(ARRAY(String)), default_factory=list
    )
    image_url: List[str] = Field(
        sa_column=Column(ARRAY(String)), default_factory=list
    )


class RecipeCreate(SQLModel):
    """레시피 생성 요청 모델"""
    recipe_pat: str
    method: str
    recipe_name: str
    thumbnail_url: str
    instructions: List[str] = []
    material_names: List[str] = []
    image_url: List[str] = []


class RecipeResponse(RecipeBase):
    instructions: List[str]
    material_names: List[str]
    image_url: List[str]


class RecipeRecommendationBase(SQLModel):
    """레시피 추천 기록 기본 모델"""
    user_id: str = Field(index=True)
    recipe_id: int = Field(foreign_key="recipe.recipe_id")
    liked: Optional[bool] = Field(default=None)  # 피드백 (true: 좋아요, false: 싫어요, null: 미응답)


class RecipeRecommendation(RecipeRecommendationBase, table=True):
    """레시피 추천 기록 테이블"""
    __tablename__ = "recipe_recommendations"

    id: Optional[int] = Field(default=None, primary_key=True)


class RecipeRecommendationRequest(SQLModel):
    """레시피 추천 요청 모델"""
    user_id: str
    limit: int = 10
    min_match_ratio: float = 0.3  # 최소 재료 일치율 (0.0 ~ 1.0)


class RecipeRecommendationResponse(SQLModel):
    """레시피 추천 응답 모델"""
    id: int                           # recommendation id
    recipe_id: int
    recipe_name: str
    thumbnail_url: str
    recipe_pat: str
    method: str
    matched_materials: List[str]      # 일치하는 재료 목록
    missing_materials: List[str]      # 부족한 재료 목록
    high_priority_materials: List[str]  # HIGH priority 재료


class RecommendationListResponse(SQLModel):
    result: list[RecipeRecommendationResponse]


class RecipeFeedbackRequest(SQLModel):
    """레시피 피드백 요청 모델"""
    user_id: str
    liked: bool  # true: 좋아요, false: 싫어요


class RecipeFeedbackResponse(SQLModel):
    """레시피 피드백 응답 모델"""
    id: int                     # 해당 레시피 추천 엔티티의 id
    user_id: str
    recipe_id: int              # 해당 레시피의 id
    liked: bool


class ExpiryEstimationRequest(SQLModel):
    """소비기한 추정 요청 모델"""
    name: str
    category: str
    purchased_at: datetime


class ExpiryEstimationResponse(SQLModel):
    """소비기한 추정 응답 모델"""
    estimated_expiration_date: datetime
    confidence: float
    notes: str
