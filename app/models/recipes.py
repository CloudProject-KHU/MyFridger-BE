from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, ARRAY, String


class RecipeBase(SQLModel):
    recipe_id: Optional[int] = Field(default=None, primary_key=True)
    recipe_pat: str # 국&찌개
    method: str  # 조리 방법 (예: 찌기, 볶기 등)
    name: str
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


class RecipeResponse(RecipeBase):
    instructions: List[str]
    material_names: List[str]
    image_url: List[str]
