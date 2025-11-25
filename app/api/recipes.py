from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from core.db import get_session
from models import Recipe, RecipeResponse

router = APIRouter()


@router.get("/{id}/instruction", response_model=RecipeResponse)
async def get_recipe_instruction(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    레시피 상세 정보 가져오기

    레시피 ID를 기반으로 레시피의 상세 정보(이름, 조리법, 재료, 조리 방법)를 반환합니다.
    """
    recipe = await session.get(Recipe, id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="레시피를 찾을 수 없습니다."
        )

    return RecipeResponse(
        recipe_id=recipe.recipe_id,
        recipe_pat=recipe.recipe_pat,
        method=recipe.method,
        name=recipe.name,
        instructions=recipe.instructions,
        material_names=recipe.material_names,
        image_url=recipe.image_url,
        thumbnail_url=recipe.thumbnail_url,
    )
