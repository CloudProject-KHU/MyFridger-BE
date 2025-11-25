from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.db import get_session
from models import (
    ExpirationEstimateRequest,
    ExpirationEstimateResponse,
    Recommendation,
    RecommendationResponse,
    RecommendationListResponse,
    Material,
)
# from services import ai_service

router = APIRouter()


@router.post("/expire", response_model=ExpirationEstimateResponse)
async def estimate_expiration(
    request: ExpirationEstimateRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    AI 기반 소비기한 추정 API

    식재료의 이름, 카테고리, 구매 날짜를 기반으로
    AI가 소비기한을 추정합니다.
    """
    try:
        result = await ai_service.estimate_expiration(
            name=request.name,
            category=request.category,
            purchased_at=request.purchased_at,
        )

        return ExpirationEstimateResponse(
            estimated_expiration_date = result["estimated_expiration_date"],
            confidence = result["confidence"],
            notes = result["notes"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"소비기한 추정 중 오류가 발생했습니다: {str(e)}",
        )


@router.get("/recipes", response_model=RecommendationListResponse)
async def get_recommended_recipes(
    session: AsyncSession = Depends(get_session),
):
    """
    맞춤형 추천 레시피 가져오기

    사용자의 식재료를 기반으로 AI가 추천한 레시피 목록을 반환
    
    실제로는 사용자 인증을 통해 해당 사용자의 식재료를 조회해야 하지만,
    현재는 모든 식재료를 기반으로 추천
    """
    try:
        # 사용자의 식재료 조회 (현재는 모든 식재료)
        # TODO: 사용자 인증 구현 후 user_id로 필터링
        query = select(Material)
        result = await session.execute(query)
        materials = result.scalars().all()

        # 식재료 정보를 dict로 변환
        material_dicts = [
            {"name": m.name, "quantity": m.quantity, "quantity_unit": m.quantity_unit} for m in materials
        ]

        # AI 추천 받기 e.g.[{"recipe_id":1, "name":"새우 두부 계란찜", "thumbnail_url":"s3.abcd", ...] (== [{"recipe_id": 1, "name":"레시피 이름", "thumbnail_url":"썸네일 url"}, {...}, ...])
        recommended_recipe_ids = await ai_service.recommend_recipes(material_dicts)

        # 추천 목록을 DB에 저장하고 반환
        recommendations = []
        for recipe in recommended_recipe_ids:
            # 이미 추천된 레시피인지 확인
            existing_query = select(Recommendation).where(
                Recommendation.recipe_id == recipe["recipe_id"]
            )
            existing_result = await session.execute(existing_query)
            existing = existing_result.scalar_one_or_none()

            if not existing:
                # 새로운 추천 생성
                recommendation = Recommendation(recipe_id=recipe["recipe_id"])
                session.add(recommendation)
                await session.flush()
                await session.refresh(recommendation)
            else:
                recommendation = existing

            recommendations.append(
                RecommendationResponse(
                    id=recommendation.id,
                    recipe_id=recipe["recipe_id"],
                    name=recipe["name"],
                    thumbnail_url=recipe["thumbnail_url"]
                    )
            )

        await session.commit()

        return RecommendationListResponse(result=recommendations)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"레시피 추천 중 오류가 발생했습니다: {str(e)}",
        )


@router.post("/{id}/feedback", status_code=status.HTTP_200_OK)
async def submit_feedback(
    id: int,
    feedback: bool,
    session: AsyncSession = Depends(get_session),
):
    """
    레시피 피드백 전송

    추천된 레시피에 대한 사용자의 피드백(좋아요/싫어요)을 저장합니다.
    """
    # 추천이 존재하는지 확인
    recommendation = await session.get(Recommendation, id)
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="추천을 찾을 수 없습니다."
        )

    # 이미 피드백이 있는지 확인
    query = select(Recommendation).where(Recommendation.id == id)
    result = await session.execute(query)
    existing_feedback = result.scalar_one_or_none()

    if existing_feedback:
        # 기존 피드백 업데이트
        existing_feedback.liked = feedback
        session.add(existing_feedback)

    await session.commit()

    return {"message": "피드백이 성공적으로 저장되었습니다."}
