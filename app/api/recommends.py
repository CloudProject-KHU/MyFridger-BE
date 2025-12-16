from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from app.core.auth import get_current_user
from app.core.db import get_session
from app.models.recipes import (
    RecipeRecommendationRequest,
    RecommendationListResponse,
    RecipeFeedbackRequest,
    RecipeFeedbackResponse,
    ExpiryEstimationRequest,
    ExpiryEstimationResponse,
    RecipeRecommendation
)
from app.services import (
    recipe_recommendation_service
)
from app.utils.bedrock_dependencies import get_expiry_service


router = APIRouter()


@router.post("/recipes", response_model=RecommendationListResponse)
async def get_recipe_recommendations(
    request: RecipeRecommendationRequest,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    """
    사용자 보유 식재료 기반 레시피 추천

    **Flow:**
    1. 사용자 보유 식재료 조회
    2. 유통기한 임박 식재료 우선순위 부여 (D-3: HIGH, D-7: MEDIUM, 그 외: NORMAL)
    3. RDS 레시피 데이터베이스에서 레시피 검색
    4. 매칭 점수 계산:
       - base_match_ratio: 재료 일치율 (0.0 ~ 1.0)
       - priority_weight: 우선순위 가중치 (1.0 ~ 2.0)
       - matching_score = base_match_ratio x priority_weight
    5. 점수 기준 정렬 및 상위 N개 반환
    6. RecipeRecommendation 엔티티 생성 (liked = null 초기 상태)

    **Request Body:**
    - user_id: 사용자 ID
    - limit: 추천할 레시피 수 (기본: 10)
    - min_match_ratio: 최소 재료 일치율 0.0~1.0 (기본: 0.3)

    **Response:**
    - List[RecipeRecommendationResponse]: 추천 레시피 목록
      - id: recommendation id (피드백 제공 시 사용)
      - recipe_id, recipe_name, thumbnail_url, recipe_pat, method
      - matching_score: 최종 매칭 점수
      - matched_materials: 일치하는 재료 목록
      - missing_materials: 부족한 재료 목록
      - high_priority_materials: HIGH priority 재료
    """
    try:
        recommendations = await recipe_recommendation_service.get_recipe_recommendations(
            session=session,
            user_id=user.id,
            limit=request.limit,
            min_match_ratio=request.min_match_ratio
        )

        return RecommendationListResponse(
            result=recommendations
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"레시피 추천 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/{recommendation_id}/feedback", response_model=RecipeFeedbackResponse)
async def create_recipe_feedback(
    recommendation_id: int,
    feedback: RecipeFeedbackRequest,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    """
    레시피 추천에 대한 피드백 (좋아요/싫어요) 저장

    RecipeRecommendation 엔티티의 liked 필드를 업데이트합니다.
    - liked = true: 좋아요
    - liked = false: 싫어요

    **Request Body:**
    - user_id: 사용자 ID
    - liked: bool (true: 좋아요, false: 싫어요)

    **Response:**
    - id: recommendation id
    - user_id: 사용자 ID
    - recipe_id: 레시피 ID
    - liked: 피드백 값
    """
    try:
        result = await recipe_recommendation_service.save_feedback(
            session=session,
            user_id=user.id,
            recommendation_id=recommendation_id,
            liked=feedback.liked
        )

        return RecipeFeedbackResponse(
            id=result.id,
            user_id=result.user_id,
            recipe_id=result.recipe_id,
            liked=result.liked
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"피드백 저장 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/expire", response_model=ExpiryEstimationResponse)
async def estimate_expiry_date(
    request: ExpiryEstimationRequest,
    use_ai: bool = True,
    service = Depends(get_expiry_service)  # 타입 힌트 제거 (circular import 방지)
):
    """
    AI 기반 소비기한 추정

    **Option A: Rule-Based Estimation (Optional)**
    - 카테고리별 기본 유통기한 규칙 사용
    - 빠른 응답 속도
    - 신뢰도: 중간 (0.5 ~ 0.75)

    **Option B: AI-Based Estimation (use_ai=true, Default)**
    - Amazon Bedrock (Claude) 사용
    - 더 정교한 추정
    - 신뢰도: 높음 (0.8 ~ 0.95)
    - AI 실패 시 자동으로 규칙 기반으로 폴백

    **카테고리별 기본 유통기한:**
    - 유제품: 7-14일
    - 육류: 3-5일
    - 채소: 5-10일
    - 냉동식품: 30-90일

    **Request Body:**
    - name: 식재료 이름
    - category: 카테고리
    - purchased_at: 구매일

    **Response:**
    - estimated_expiration_date: 추정된 유통기한
    - confidence: 신뢰도 (0.0 ~ 1.0)
    - notes: 추정 근거 및 보관 팁
    """
    try:
        result = await service.estimate_expiry(
            request=request,
            use_ai=use_ai
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"소비기한 추정 중 오류가 발생했습니다: {str(e)}"
        )
