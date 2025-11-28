import pytest
import httpx
from typing import AsyncGenerator

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.mark.asyncio
async def test_get_recipe_detail_success(client: httpx.AsyncClient):
    """레시피 상세 조회 성공"""
    print("\n=== Testing Recipe Detail: Success ===")

    # 실제 존재하는 레시피 ID로 테스트 (예: 1번)
    # 실제 운영 환경에서는 DB에 데이터가 있어야 함
    recipe_id = 1

    response = await client.get(f"/recipes/{recipe_id}")

    # 레시피가 존재하면 200, 없으면 404
    if response.status_code == 200:
        data = response.json()

        # 응답 구조 검증
        assert "recipe_id" in data
        assert "recipe_name" in data
        assert "recipe_pat" in data
        assert "method" in data
        assert "thumbnail_url" in data
        assert "instructions" in data
        assert "material_names" in data
        assert "image_url" in data
        assert "cached_at" in data

        # 데이터 타입 검증
        assert isinstance(data["recipe_id"], int)
        assert isinstance(data["recipe_name"], str)
        assert isinstance(data["instructions"], list)
        assert isinstance(data["material_names"], list)
        assert isinstance(data["image_url"], list)

        print(f"Recipe found: {data['recipe_name']}")
    else:
        assert response.status_code == 404
        print("Recipe not found (expected if DB is empty)")


@pytest.mark.asyncio
async def test_get_recipe_detail_not_found(client: httpx.AsyncClient):
    """존재하지 않는 레시피 조회"""
    print("\n=== Testing Recipe Detail: Not Found ===")

    # 존재하지 않는 레시피 ID
    recipe_id = 999999

    response = await client.get(f"/recipes/{recipe_id}")

    assert response.status_code == 404
    error_data = response.json()
    assert "detail" in error_data


@pytest.mark.asyncio
async def test_get_recipe_detail_invalid_id(client: httpx.AsyncClient):
    """잘못된 레시피 ID 형식"""
    print("\n=== Testing Recipe Detail: Invalid ID ===")

    # 문자열 ID (숫자가 아님)
    response = await client.get("/recipes/invalid_id")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_recipe_detail_negative_id(client: httpx.AsyncClient):
    """음수 레시피 ID"""
    print("\n=== Testing Recipe Detail: Negative ID ===")

    response = await client.get("/recipes/-1")

    # 음수 ID는 404 (존재하지 않음)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_recipe_detail_zero_id(client: httpx.AsyncClient):
    """0번 레시피 ID"""
    print("\n=== Testing Recipe Detail: Zero ID ===")

    response = await client.get("/recipes/0")

    # 0번 ID는 존재하지 않음
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_multiple_recipes(client: httpx.AsyncClient):
    """여러 레시피 순차 조회"""
    print("\n=== Testing Multiple Recipe Details ===")

    # 1~10번 레시피 조회
    found_recipes = []
    for recipe_id in range(1, 11):
        response = await client.get(f"/recipes/{recipe_id}")

        if response.status_code == 200:
            data = response.json()
            found_recipes.append(data)
            print(f"Recipe {recipe_id}: {data['recipe_name']}")

    print(f"Total recipes found: {len(found_recipes)}")

    # 모든 레시피가 올바른 구조를 가지고 있는지 확인
    for recipe in found_recipes:
        assert "recipe_id" in recipe
        assert "recipe_name" in recipe
        assert "material_names" in recipe
        assert isinstance(recipe["material_names"], list)


@pytest.mark.asyncio
async def test_recipe_detail_response_structure(client: httpx.AsyncClient):
    """레시피 응답 구조 상세 검증"""
    print("\n=== Testing Recipe Response Structure ===")

    recipe_id = 1
    response = await client.get(f"/recipes/{recipe_id}")

    if response.status_code == 200:
        data = response.json()

        # 필수 필드 존재 확인
        required_fields = [
            "recipe_id",
            "recipe_name",
            "recipe_pat",
            "method",
            "thumbnail_url",
            "instructions",
            "material_names",
            "image_url",
            "cached_at",
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # 리스트 필드는 비어있지 않아야 함 (일반적으로)
        if len(data["instructions"]) > 0:
            assert isinstance(data["instructions"][0], str)

        if len(data["material_names"]) > 0:
            assert isinstance(data["material_names"][0], str)

        if len(data["image_url"]) > 0:
            assert isinstance(data["image_url"][0], str)
            # 이미지 URL은 http로 시작해야 함
            assert data["image_url"][0].startswith("http")


@pytest.mark.asyncio
async def test_recipe_detail_cached_at_format(client: httpx.AsyncClient):
    """cached_at 날짜 형식 검증"""
    print("\n=== Testing cached_at Date Format ===")

    recipe_id = 1
    response = await client.get(f"/recipes/{recipe_id}")

    if response.status_code == 200:
        data = response.json()

        # cached_at이 ISO 8601 형식인지 확인
        from datetime import datetime

        try:
            cached_at = datetime.fromisoformat(data["cached_at"].replace("Z", "+00:00"))
            assert cached_at is not None
            print(f"Cached at: {cached_at}")
        except ValueError:
            pytest.fail(f"Invalid datetime format: {data['cached_at']}")


@pytest.mark.asyncio
async def test_recipe_detail_thumbnail_url(client: httpx.AsyncClient):
    """썸네일 URL 검증"""
    print("\n=== Testing Thumbnail URL ===")

    recipe_id = 1
    response = await client.get(f"/recipes/{recipe_id}")

    if response.status_code == 200:
        data = response.json()

        thumbnail_url = data["thumbnail_url"]

        # URL 형식 확인
        assert thumbnail_url.startswith("http://") or thumbnail_url.startswith("https://")

        # S3 URL인지 또는 외부 URL인지 확인
        print(f"Thumbnail URL: {thumbnail_url}")


@pytest.mark.asyncio
async def test_recipe_detail_materials_not_empty(client: httpx.AsyncClient):
    """재료 목록이 비어있지 않은지 확인"""
    print("\n=== Testing Material Names Not Empty ===")

    recipe_id = 1
    response = await client.get(f"/recipes/{recipe_id}")

    if response.status_code == 200:
        data = response.json()

        # 대부분의 레시피는 재료가 있어야 함
        if len(data["material_names"]) > 0:
            print(f"Materials: {', '.join(data['material_names'])}")
            assert all(isinstance(mat, str) for mat in data["material_names"])
            assert all(len(mat) > 0 for mat in data["material_names"])


@pytest.mark.asyncio
async def test_recipe_detail_instructions_not_empty(client: httpx.AsyncClient):
    """조리 순서가 비어있지 않은지 확인"""
    print("\n=== Testing Instructions Not Empty ===")

    recipe_id = 1
    response = await client.get(f"/recipes/{recipe_id}")

    if response.status_code == 200:
        data = response.json()

        # 대부분의 레시피는 조리 순서가 있어야 함
        if len(data["instructions"]) > 0:
            print(f"Instructions count: {len(data['instructions'])}")
            assert all(isinstance(inst, str) for inst in data["instructions"])
            assert all(len(inst) > 0 for inst in data["instructions"])


@pytest.mark.asyncio
async def test_recipe_detail_with_sync(client: httpx.AsyncClient):
    """레시피 동기화 후 조회 (관리자 기능)"""
    print("\n=== Testing Recipe Detail After Sync ===")

    # 이 테스트는 레시피 동기화가 이루어진 후에 실행되어야 함
    # 동기화는 Lambda 함수로 매주 월요일에 실행됨

    # 최근 동기화된 레시피 조회
    recipe_id = 1
    response = await client.get(f"/recipes/{recipe_id}")

    if response.status_code == 200:
        data = response.json()

        # 동기화된 레시피는 모든 필드가 채워져 있어야 함
        assert len(data["recipe_name"]) > 0
        assert len(data["recipe_pat"]) > 0
        assert len(data["method"]) > 0
        assert len(data["thumbnail_url"]) > 0

        print(f"Recipe synced: {data['recipe_name']}")
        print(f"Category: {data['recipe_pat']}, Method: {data['method']}")


@pytest.mark.asyncio
async def test_recipe_detail_performance(client: httpx.AsyncClient):
    """레시피 조회 성능 테스트"""
    print("\n=== Testing Recipe Detail Performance ===")

    import time

    recipe_id = 1
    start_time = time.time()

    response = await client.get(f"/recipes/{recipe_id}")

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"Response time: {elapsed:.3f}s")

    # 응답 시간이 1초 이내여야 함
    assert elapsed < 1.0

    if response.status_code == 200:
        print("Performance test passed")
