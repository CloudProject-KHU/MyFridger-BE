import pytest
import httpx
from typing import AsyncGenerator
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.mark.asyncio
async def test_estimate_expiry_apple(client: httpx.AsyncClient):
    """사과 소비기한 추정"""
    print("\n=== Testing Expiry Estimation: Apple ===")

    purchased_at = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    response = await client.post(
        "/recommends/expire",
        json={
            "name": "사과",
            "category": "과일",
            "purchased_at": purchased_at.isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "estimated_expiration_date" in data
    assert "confidence" in data
    assert "notes" in data

    # 소비기한이 구매일보다 미래여야 함
    expiry_date = datetime.fromisoformat(data["estimated_expiration_date"].replace("Z", "+00:00"))
    assert expiry_date > purchased_at

    # 신뢰도 범위 확인 (0.0 ~ 1.0)
    assert 0.0 <= data["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_estimate_expiry_milk(client: httpx.AsyncClient):
    """우유 소비기한 추정"""
    print("\n=== Testing Expiry Estimation: Milk ===")

    purchased_at = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    response = await client.post(
        "/recommends/expire",
        json={
            "name": "우유",
            "category": "유제품",
            "purchased_at": purchased_at.isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()

    # 유제품은 약 5일 정도
    expiry_date = datetime.fromisoformat(data["estimated_expiration_date"].replace("Z", "+00:00"))
    days_diff = (expiry_date - purchased_at).days
    assert 3 <= days_diff <= 7  # 3~7일 사이


@pytest.mark.asyncio
async def test_estimate_expiry_meat(client: httpx.AsyncClient):
    """육류 소비기한 추정"""
    print("\n=== Testing Expiry Estimation: Meat ===")

    purchased_at = datetime.now(timezone.utc)

    response = await client.post(
        "/recommends/expire",
        json={
            "name": "소고기",
            "category": "육류",
            "purchased_at": purchased_at.isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()

    # 육류는 약 3일
    expiry_date = datetime.fromisoformat(data["estimated_expiration_date"].replace("Z", "+00:00"))
    days_diff = (expiry_date - purchased_at).days
    assert 2 <= days_diff <= 5


@pytest.mark.asyncio
async def test_estimate_expiry_seafood(client: httpx.AsyncClient):
    """해산물 소비기한 추정"""
    print("\n=== Testing Expiry Estimation: Seafood ===")

    purchased_at = datetime.now(timezone.utc)

    response = await client.post(
        "/recommends/expire",
        json={
            "name": "고등어",
            "category": "해산물",
            "purchased_at": purchased_at.isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()

    # 해산물은 약 2일
    expiry_date = datetime.fromisoformat(data["estimated_expiration_date"].replace("Z", "+00:00"))
    days_diff = (expiry_date - purchased_at).days
    assert 1 <= days_diff <= 3


@pytest.mark.asyncio
async def test_estimate_expiry_vegetable(client: httpx.AsyncClient):
    """채소 소비기한 추정"""
    print("\n=== Testing Expiry Estimation: Vegetable ===")

    purchased_at = datetime.now(timezone.utc)

    response = await client.post(
        "/recommends/expire",
        json={
            "name": "배추",
            "category": "채소",
            "purchased_at": purchased_at.isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()

    # 채소는 약 5일
    expiry_date = datetime.fromisoformat(data["estimated_expiration_date"].replace("Z", "+00:00"))
    days_diff = (expiry_date - purchased_at).days
    assert 3 <= days_diff <= 7


@pytest.mark.asyncio
async def test_estimate_expiry_unknown_category(client: httpx.AsyncClient):
    """알 수 없는 카테고리"""
    print("\n=== Testing Expiry Estimation: Unknown Category ===")

    purchased_at = datetime.now(timezone.utc)

    response = await client.post(
        "/recommends/expire",
        json={
            "name": "신비한 식재료",
            "category": "기타",
            "purchased_at": purchased_at.isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()

    # 기본 추정값 반환
    assert "estimated_expiration_date" in data
    assert data["confidence"] >= 0.0


@pytest.mark.asyncio
async def test_estimate_expiry_missing_field(client: httpx.AsyncClient):
    """필수 필드 누락"""
    print("\n=== Testing Expiry Estimation: Missing Field ===")

    # name 필드 누락
    response = await client.post(
        "/recommends/expire",
        json={
            "category": "과일",
            "purchased_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_estimate_expiry_invalid_date(client: httpx.AsyncClient):
    """잘못된 날짜 형식"""
    print("\n=== Testing Expiry Estimation: Invalid Date ===")

    response = await client.post(
        "/recommends/expire",
        json={
            "name": "사과",
            "category": "과일",
            "purchased_at": "invalid-date",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_estimate_expiry_future_purchased_date(client: httpx.AsyncClient):
    """미래 구매일자 (유효한 요청)"""
    print("\n=== Testing Expiry Estimation: Future Purchase Date ===")

    future_date = datetime.now(timezone.utc) + timedelta(days=10)

    response = await client.post(
        "/recommends/expire",
        json={
            "name": "사과",
            "category": "과일",
            "purchased_at": future_date.isoformat(),
        },
    )

    # 미래 날짜도 유효한 요청 (예: 예정된 구매)
    assert response.status_code == 200
    data = response.json()

    expiry_date = datetime.fromisoformat(data["estimated_expiration_date"].replace("Z", "+00:00"))
    assert expiry_date > future_date


@pytest.mark.asyncio
async def test_estimate_expiry_different_categories(client: httpx.AsyncClient):
    """여러 카테고리 비교 테스트"""
    print("\n=== Testing Expiry Estimation: Multiple Categories ===")

    purchased_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    categories = [
        ("사과", "과일"),
        ("우유", "유제품"),
        ("소고기", "육류"),
        ("고등어", "해산물"),
        ("배추", "채소"),
    ]

    results = []
    for name, category in categories:
        response = await client.post(
            "/recommends/expire",
            json={
                "name": name,
                "category": category,
                "purchased_at": purchased_at.isoformat(),
            },
        )
        assert response.status_code == 200
        data = response.json()
        expiry_date = datetime.fromisoformat(
            data["estimated_expiration_date"].replace("Z", "+00:00")
        )
        days_diff = (expiry_date - purchased_at).days
        results.append((name, category, days_diff, data["confidence"]))

    # 해산물이 가장 짧은 소비기한을 가져야 함
    seafood_days = next(days for name, cat, days, conf in results if cat == "해산물")
    other_days = [days for name, cat, days, conf in results if cat != "해산물"]
    assert seafood_days <= min(other_days)


@pytest.mark.asyncio
async def test_estimate_expiry_consistency(client: httpx.AsyncClient):
    """동일한 입력에 대한 일관성 테스트"""
    print("\n=== Testing Expiry Estimation: Consistency ===")

    request_data = {
        "name": "사과",
        "category": "과일",
        "purchased_at": datetime(2025, 1, 1, tzinfo=timezone.utc).isoformat(),
    }

    # 동일한 요청 3번
    results = []
    for _ in range(3):
        response = await client.post("/recommends/expire", json=request_data)
        assert response.status_code == 200
        results.append(response.json())

    # 모든 결과가 동일해야 함 (규칙 기반 추정)
    first_result = results[0]["estimated_expiration_date"]
    for result in results[1:]:
        assert result["estimated_expiration_date"] == first_result


@pytest.mark.asyncio
async def test_estimate_expiry_with_material_creation(client: httpx.AsyncClient):
    """식재료 생성과 함께 소비기한 추정"""
    print("\n=== Testing Expiry Estimation with Material Creation ===")

    user_id = "expiry_test_user"
    purchased_at = datetime.now(timezone.utc)

    # 1. 소비기한 추정
    estimate_response = await client.post(
        "/recommends/expire",
        json={
            "name": "토마토",
            "category": "채소",
            "purchased_at": purchased_at.isoformat(),
        },
    )

    assert estimate_response.status_code == 200
    estimated_expiry = estimate_response.json()["estimated_expiration_date"]

    # 2. 추정된 소비기한으로 식재료 생성
    material_response = await client.post(
        "/materials/manual",
        json={
            "user_id": user_id,
            "name": "토마토",
            "price": 3000,
            "category": "채소",
            "purchased_at": purchased_at.isoformat(),
            "expired_at": estimated_expiry,
            "quantity": 3,
        },
    )

    assert material_response.status_code == 201
    material_id = material_response.json()["id"]

    # 3. 생성된 식재료 확인
    get_response = await client.get(f"/materials/{material_id}")
    assert get_response.status_code == 200
    material_data = get_response.json()
    assert material_data["expired_at"] == estimated_expiry

    # Cleanup
    await client.delete(f"/materials/{material_id}")


@pytest.mark.asyncio
async def test_estimate_expiry_empty_string_name(client: httpx.AsyncClient):
    """빈 문자열 이름"""
    print("\n=== Testing Expiry Estimation: Empty Name ===")

    response = await client.post(
        "/recommends/expire",
        json={
            "name": "",
            "category": "과일",
            "purchased_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_estimate_expiry_special_characters(client: httpx.AsyncClient):
    """특수 문자 포함 이름"""
    print("\n=== Testing Expiry Estimation: Special Characters ===")

    response = await client.post(
        "/recommends/expire",
        json={
            "name": "사과@#$%",
            "category": "과일",
            "purchased_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    # 특수 문자가 있어도 유효한 요청
    assert response.status_code == 200
    data = response.json()
    assert "estimated_expiration_date" in data
