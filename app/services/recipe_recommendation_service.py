from datetime import datetime
from typing import List, Dict
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.recipes import (
    Priority,
    Recipe,
    RecipeRecommendation,
    RecipeRecommendationResponse
)
from app.models.materials import Material


# Priority별 가중치 상수
PRIORITY_WEIGHTS = {
    Priority.HIGH: 2.0,    # 긴급 식재료 사용 시 2배 가중
    Priority.MEDIUM: 1.3,  # 임박 식재료 사용 시 1.3배 가중
    Priority.NORMAL: 1.0   # 기본 가중치
}


class RecipeRecommendationService:
    """레시피 추천 서비스 (단순화)"""

    async def assign_material_priority(self, material: Material) -> Priority:
        """
        식재료별 Priority 부여
        유통기한에 따라 HIGH(D-3), MEDIUM(D-7), NORMAL로 분류
        """
        if not material.expired_at:
            return Priority.NORMAL

        now = datetime.utcnow()
        days_until_expiry = (material.expired_at.replace(tzinfo=None) - now).days

        if days_until_expiry <= 3:
            return Priority.HIGH
        elif days_until_expiry <= 7:
            return Priority.MEDIUM
        else:
            return Priority.NORMAL

    async def get_user_materials(
        self,
        session: AsyncSession,
        user_id: str
    ) -> List[Material]:
        """사용자 보유 식재료 조회"""
        query = select(Material).where(Material.user_id == user_id)
        result = await session.execute(query)
        return result.scalars().all()

    async def calculate_matching_score(
        self,
        recipe: Recipe,
        user_materials: List[Material],
        material_priorities: Dict[str, Priority]
    ) -> Dict:
        """
        레시피 매칭 점수 계산 (단순화)

        Returns:
            - matching_score: 최종 점수 (base_match_ratio × priority_weight)
            - base_match_ratio: 일치 재료 수 / 전체 필요 재료 수
            - matched_materials: 일치하는 재료 목록
            - missing_materials: 부족한 재료 목록
            - high_priority_materials: HIGH priority 재료 목록
        """
        # 1. 재료 일치율 계산 (부분 문자열 매칭)
        recipe_ingredients = set(m.lower() for m in recipe.material_names)
        user_ingredient_names = set(m.name.lower() for m in user_materials)

        # 부분 문자열 매칭: 사용자 재료가 레시피 재료에 포함되어 있는지 확인
        matched = set()
        for user_ingredient in user_ingredient_names:
            for recipe_ingredient in recipe_ingredients:
                if user_ingredient in recipe_ingredient:
                    matched.add(user_ingredient)
                    break

        if not recipe_ingredients:
            base_match_ratio = 0.0
        else:
            base_match_ratio = len(matched) / len(recipe_ingredients)

        # 2. priority_weight 계산: 매칭된 재료 중 최고 Priority 기준
        matched_materials_list = [
            m for m in user_materials
            if m.name.lower() in matched
        ]

        if matched_materials_list:
            highest_priority = max(
                material_priorities.get(m.name, Priority.NORMAL)
                for m in matched_materials_list
            )
            priority_weight = PRIORITY_WEIGHTS[highest_priority]
        else:
            priority_weight = 1.0

        # 3. 최종 점수 = base_match_ratio × priority_weight
        final_score = base_match_ratio * priority_weight

        # 매칭 재료 및 부족 재료 목록
        matched_materials = list(matched)
        missing_materials = list(recipe_ingredients - user_ingredient_names)

        # HIGH priority 재료 목록
        high_priority_materials = [
            m.name for m in user_materials
            if material_priorities.get(m.name, Priority.NORMAL) == Priority.HIGH
            and m.name.lower() in matched
        ]

        return {
            "matching_score": final_score,
            "base_match_ratio": base_match_ratio,
            "matched_materials": matched_materials,
            "missing_materials": missing_materials,
            "high_priority_materials": high_priority_materials
        }

    async def get_recipe_recommendations(
        self,
        session: AsyncSession,
        user_id: str,
        limit: int = 10,
        min_match_ratio: float = 0.3
    ) -> List[RecipeRecommendationResponse]:
        """
        사용자에게 레시피 추천 (단순화)

        1. 사용자 보유 식재료 조회
        2. 유통기한 임박 식재료 Priority 부여
        3. RDS 레시피 데이터베이스에서 레시피 검색
        4. 매칭 점수 계산 (base_match_ratio × priority_weight)
        5. 점수 기준 정렬 및 상위 N개 반환
        """
        # Step 1: 사용자 보유 식재료 조회
        user_materials = await self.get_user_materials(session, user_id)

        if not user_materials:
            return []

        # Step 2: 유통기한 임박 식재료 우선순위 부여
        material_priorities = {}
        for material in user_materials:
            priority = await self.assign_material_priority(material)
            material_priorities[material.name] = priority

        # Step 3: RDS 레시피 데이터베이스에서 레시피 검색
        query = select(Recipe)
        result = await session.execute(query)
        all_recipes = result.scalars().all()

        # Step 4: 매칭 점수 계산
        scored_recipes = []
        for recipe in all_recipes:
            score_info = await self.calculate_matching_score(
                recipe, user_materials, material_priorities
            )

            # 최소 일치율 필터링
            # base_match = score_info["matching_score"] / max(
            #     PRIORITY_WEIGHTS[Priority.HIGH],
            #     PRIORITY_WEIGHTS[Priority.MEDIUM],
            #     PRIORITY_WEIGHTS[Priority.NORMAL]
            # )
            # if base_match < min_match_ratio:
            #     continue
            if score_info["base_match_ratio"] < min_match_ratio:
                continue

            scored_recipes.append({
                "recipe": recipe,
                "score_info": score_info
            })

        # Step 5: 점수 기준 정렬
        scored_recipes.sort(key=lambda x: x["score_info"]["matching_score"], reverse=True)

        # 상위 N개 선택
        top_recipes = scored_recipes[:limit]

        # DB에 추천 기록 저장 및 응답 생성
        recommendations = []
        for item in top_recipes:
            recipe = item["recipe"]
            score_info = item["score_info"]

            # DB에 추천 기록 저장 (liked = null 초기 상태)
            recommendation = RecipeRecommendation(
                user_id=user_id,
                recipe_id=recipe.recipe_id,
                liked=None
            )
            session.add(recommendation)
            await session.flush()  # ID를 받기 위해 flush

            # 응답 객체 생성
            recommendations.append(RecipeRecommendationResponse(
                id=recommendation.id,
                recipe_id=recipe.recipe_id,
                recipe_name=recipe.recipe_name,
                thumbnail_url=recipe.thumbnail_url,
                recipe_pat=recipe.recipe_pat,
                method=recipe.method,
                matched_materials=score_info["matched_materials"],
                missing_materials=score_info["missing_materials"],
                high_priority_materials=score_info["high_priority_materials"]
            ))

        await session.commit()

        return recommendations

    async def save_feedback(
        self,
        session: AsyncSession,
        user_id: str,
        recommendation_id: int,
        liked: bool
    ) -> RecipeRecommendation:
        """
        레시피 피드백 저장 (단순화)
        RecipeRecommendation의 liked 필드만 업데이트
        """
        # 추천 기록 조회
        recommendation = await session.get(RecipeRecommendation, recommendation_id)

        if not recommendation:
            raise ValueError(f"Recommendation {recommendation_id} not found")

        if recommendation.user_id != user_id:
            raise ValueError("User ID mismatch")

        # liked 업데이트
        recommendation.liked = liked

        await session.commit()
        await session.refresh(recommendation)

        return recommendation


recipe_recommendation_service = RecipeRecommendationService()
