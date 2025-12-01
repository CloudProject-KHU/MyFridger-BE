import pytest
import httpx
from typing import AsyncGenerator
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture
async def test_user_materials(client: httpx.AsyncClient):
    """테스트용 사용자 식재료 생성"""
    user_id = "test_user_123"
    now = datetime.now(timezone.utc)

    # 식재료 생성
    materials = []

    # HIGH priority 식재료 (D-2)
    response = await client.post(
        "/materials/manual",
        json={
            "user_id": user_id,
            "name": "사과",
            "price": 1000,
            "category": "과일",
            "purchased_at": now.isoformat(),
            "expired_at": (now + timedelta(days=2)).isoformat(),
            "quantity": 5,
        },
    )
    if response.status_code == 201:
        materials.append(response.json()["id"])

    # MEDIUM priority 식재료 (D-5)
    response = await client.post(
        "/materials/manual",
        json={
            "user_id": user_id,
            "name": "우유",
            "price": 2000,
            "category": "유제품",
            "purchased_at": now.isoformat(),
            "expired_at": (now + timedelta(days=5)).isoformat(),
            "quantity": 1,
        },
    )
    if response.status_code == 201:
        materials.append(response.json()["id"])

    # NORMAL priority 식재료 (D-10)
    response = await client.post(
        "/materials/manual",
        json={
            "user_id": user_id,
            "name": "계란",
            "price": 3000,
            "category": "계란",
            "purchased_at": now.isoformat(),
            "expired_at": (now + timedelta(days=10)).isoformat(),
            "quantity": 12,
        },
    )
    if response.status_code == 201:
        materials.append(response.json()["id"])

    yield {"user_id": user_id, "material_ids": materials}

    # Cleanup
    for material_id in materials:
        await client.delete(f"/materials/{material_id}")


@pytest.mark.asyncio
async def test_get_recipe_recommendations_success(client: httpx.AsyncClient, test_user_materials):
    """레시피 추천 성공"""
    print("\n=== Testing Recipe Recommendations ===")

    user_id = test_user_materials["user_id"]

    response = await client.post(
        f"/recommends/recipes",
        json={"user_id": user_id, "limit": 10, "min_match_ratio": 0.3}
    )

    assert response.status_code == 200
    data = response.json()

    assert "result" in data
    recommendations = data["result"]

    # 추천 결과 검증
    if len(recommendations) > 0:
        first_rec = recommendations[0]
        assert "id" in first_rec
        assert "recipe_id" in first_rec
        assert "recipe_name" in first_rec
        assert "thumbnail_url" in first_rec
        assert "matched_materials" in first_rec
        assert "missing_materials" in first_rec
        assert "high_priority_materials" in first_rec


@pytest.mark.asyncio
async def test_get_recipe_recommendations_empty_materials(client: httpx.AsyncClient):
    """식재료가 없는 사용자"""
    print("\n=== Testing Recipe Recommendations (No Materials) ===")

    response = await client.post(
        f"/recommends/recipes",
        json={"user_id": "empty_user", "limit": 10}
    )

    assert response.status_code == 200
    data = response.json()

    # 식재료가 없으면 추천 결과도 없음
    assert data["result"] == []


@pytest.mark.asyncio
async def test_get_recipe_recommendations_high_min_match_ratio(
    client: httpx.AsyncClient, test_user_materials
):
    """높은 최소 일치율 설정"""
    print("\n=== Testing Recipe Recommendations (High Min Match Ratio) ===")

    user_id = test_user_materials["user_id"]

    # 최소 일치율 80%로 설정
    response = await client.post(
        f"/recommends/recipes",
        json={"user_id": user_id, "limit": 10, "min_match_ratio": 0.8}
    )

    assert response.status_code == 200
    data = response.json()

    # 매칭률이 높은 레시피만 추천
    for rec in data["result"]:
        total_materials = len(rec["matched_materials"]) + len(rec["missing_materials"])
        if total_materials > 0:
            match_ratio = len(rec["matched_materials"]) / total_materials
            assert match_ratio >= 0.8


@pytest.mark.asyncio
async def test_get_recipe_recommendations_limit(
    client: httpx.AsyncClient, test_user_materials
):
    """추천 개수 제한"""
    print("\n=== Testing Recipe Recommendations (Limit) ===")

    user_id = test_user_materials["user_id"]

    response = await client.post(
        f"/recommends/recipes",
        json={"user_id": user_id, "limit": 3}
    )

    assert response.status_code == 200
    data = response.json()

    # 최대 3개까지만 추천
    assert len(data["result"]) <= 3


@pytest.mark.asyncio
async def test_recipe_feedback_success(client: httpx.AsyncClient, test_user_materials):
    """레시피 피드백 저장 성공"""
    print("\n=== Testing Recipe Feedback ===")

    user_id = test_user_materials["user_id"]

    # 먼저 추천 받기
    response = await client.post(
        f"/recommends/recipes",
        json={"user_id": user_id, "limit": 1}
    )

    if response.status_code == 200 and len(response.json()["result"]) > 0:
        recommendation_id = response.json()["result"][0]["id"]

        # 피드백 저장 (좋아요)
        feedback_response = await client.post(
            f"/recommends/recipes/{recommendation_id}/feedback",
            json={"user_id": user_id, "liked": True}
        )

        assert feedback_response.status_code == 200
        feedback_data = feedback_response.json()

        assert feedback_data["id"] == recommendation_id
        assert feedback_data["liked"] is True


@pytest.mark.asyncio
async def test_recipe_feedback_not_found(client: httpx.AsyncClient):
    """존재하지 않는 추천 ID"""
    print("\n=== Testing Recipe Feedback (Not Found) ===")

    response = await client.post(
        f"/recommends/recipes/999999/feedback",
        json={"user_id": "test_user", "liked": True}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_recipe_feedback_user_mismatch(client: httpx.AsyncClient, test_user_materials):
    """다른 사용자의 추천에 피드백"""
    print("\n=== Testing Recipe Feedback (User Mismatch) ===")

    user_id = test_user_materials["user_id"]

    # 추천 받기
    response = await client.post(
        f"/recommends/recipes",
        json={"user_id": user_id, "limit": 1}
    )

    if response.status_code == 200 and len(response.json()["result"]) > 0:
        recommendation_id = response.json()["result"][0]["id"]

        # 다른 사용자로 피드백 시도
        feedback_response = await client.post(
            f"/recommends/recipes/{recommendation_id}/feedback",
            json={"user_id": "other_user", "liked": True}
        )

        assert feedback_response.status_code in [400, 403, 404]


@pytest.mark.asyncio
async def test_recipe_feedback_update(client: httpx.AsyncClient, test_user_materials):
    """피드백 업데이트 (좋아요 -> 싫어요)"""
    print("\n=== Testing Recipe Feedback Update ===")

    user_id = test_user_materials["user_id"]

    # 추천 받기
    response = await client.post(
        f"/recommends/recipes",
        json={"user_id": user_id, "limit": 1}
    )

    if response.status_code == 200 and len(response.json()["result"]) > 0:
        recommendation_id = response.json()["result"][0]["id"]

        # 좋아요
        await client.post(
            f"/recommends/recipes/{recommendation_id}/feedback",
            json={"user_id": user_id, "liked": True}
        )

        # 싫어요로 변경
        feedback_response = await client.post(
            f"/recommends/recipes/{recommendation_id}/feedback",
            json={"user_id": user_id, "liked": False}
        )

        assert feedback_response.status_code == 200
        assert feedback_response.json()["liked"] is False


@pytest.mark.asyncio
async def test_recipe_recommendations_with_high_priority_materials(
    client: httpx.AsyncClient, test_user_materials
):
    """HIGH priority 식재료가 포함된 추천"""
    print("\n=== Testing High Priority Materials in Recommendations ===")

    user_id = test_user_materials["user_id"]

    response = await client.post(
        f"/recommends/recipes",
        json={"user_id": user_id, "limit": 10, "min_match_ratio": 0.3}
    )

    assert response.status_code == 200
    recommendations = response.json()["result"]

    # HIGH priority 식재료를 포함한 레시피가 우선순위가 높아야 함
    for rec in recommendations:
        if len(rec["high_priority_materials"]) > 0:
            # "사과"가 HIGH priority이므로 포함되어 있어야 함
            assert any("사과" in mat.lower() for mat in rec["high_priority_materials"])


@pytest.mark.asyncio
async def test_recipe_recommendations_invalid_params(client: httpx.AsyncClient):
    """잘못된 파라미터"""
    print("\n=== Testing Invalid Parameters ===")

    # 음수 limit
    response = await client.post(
        f"/recommends/recipes",
        json={"user_id": "test_user", "limit": -1}
    )
    assert response.status_code == 422

    # min_match_ratio가 범위 초과 (0.0~1.0 벗어남)
    response = await client.post(
        f"/recommends/recipes",
        json={"user_id": "test_user", "min_match_ratio": 1.5}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_recipe_recommendations_missing_user_id(client: httpx.AsyncClient):
    """user_id 누락"""
    print("\n=== Testing Missing User ID ===")

    response = await client.post(f"/recommends/recipes", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_full_recommendation_workflow(client: httpx.AsyncClient):
    """전체 추천 워크플로우 테스트"""
    print("\n=== Testing Full Recommendation Workflow ===")

    user_id = "workflow_test_user"
    now = datetime.now(timezone.utc)

    # 1. 식재료 추가
    material_ids = []
    for i, (name, days) in enumerate([("토마토", 2), ("양파", 5), ("마늘", 10)]):
        response = await client.post(
            "/materials/manual",
            json={
                "user_id": user_id,
                "name": name,
                "price": 1000 * (i + 1),
                "category": "채소",
                "purchased_at": now.isoformat(),
                "expired_at": (now + timedelta(days=days)).isoformat(),
                "quantity": 1,
            },
        )
        if response.status_code == 201:
            material_ids.append(response.json()["id"])

    # 2. 레시피 추천 받기
    rec_response = await client.post(
        f"/recommends/recipes",
        json={"user_id": user_id, "limit": 5, "min_match_ratio": 0.3}
    )
    assert rec_response.status_code == 200
    recommendations = rec_response.json()["result"]

    # 3. 첫 번째 추천에 피드백
    if len(recommendations) > 0:
        recommendation_id = recommendations[0]["id"]
        feedback_response = await client.post(
            f"/recommends/recipes/{recommendation_id}/feedback",
            json={"user_id": user_id, "liked": True}
        )
        assert feedback_response.status_code == 200

    # 4. Cleanup
    for material_id in material_ids:
        await client.delete(f"/materials/{material_id}")
