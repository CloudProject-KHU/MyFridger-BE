import pytest
import httpx
from typing import AsyncGenerator

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        yield client


@pytest.mark.asyncio
async def test_materials_crud_flow(client: httpx.AsyncClient):
    print("\n=== Testing CRUD Flow ===")

    # 1. Create Material
    print("1. Create Material")
    response = await client.post(
        "/materials/manual",
        json={
            "user_id": "test_user",
            "name": "Milk",
            "price": 3000,
            "category": "Dairy",
            "purchased_at": "2023-10-27T10:00:00",
            "expired_at": "2023-11-05T10:00:00",
            "quantity": 1,
            "quantity_unit": "L",
        },
    )
    assert response.status_code == 201
    data = response.json()
    material_id = data["id"]
    assert data["name"] == "Milk"

    # 2. Get List
    print("2. Get List")
    response = await client.get("/materials")
    assert response.status_code == 200
    assert len(response.json()["result"]) > 0

    # 3. Get Detail
    print(f"3. Get Detail {material_id}")
    response = await client.get(f"/materials/{material_id}")
    assert response.status_code == 200
    assert response.json()["id"] == material_id

    # 4. Update
    print(f"4. Update {material_id}")
    response = await client.patch(f"/materials/{material_id}", json={"price": 3500})
    assert response.status_code == 200
    assert response.json()["price"] == 3500

    # 5. Delete
    print(f"5. Delete {material_id}")
    response = await client.delete(f"/materials/{material_id}")
    assert response.status_code == 204

    # 6. Verify Delete
    print("6. Verify Delete")
    response = await client.get(f"/materials/{material_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_missing_field(client: httpx.AsyncClient):
    print("\n=== Testing Failure: Missing Field ===")
    response = await client.post(
        "/materials/manual",
        json={
            "price": 3000,
            "category": "Dairy",
            "purchased_at": "2023-10-27T10:00:00",
            "expired_at": "2023-11-05T10:00:00",
            "quantity": 1,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_invalid_type(client: httpx.AsyncClient):
    print("\n=== Testing Failure: Invalid Type ===")
    response = await client.post(
        "/materials/manual",
        json={
            "name": "Bad Price Milk",
            "price": "expensive",
            "category": "Dairy",
            "purchased_at": "2023-10-27T10:00:00",
            "expired_at": "2023-11-05T10:00:00",
            "quantity": 1,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_non_existent(client: httpx.AsyncClient):
    print("\n=== Testing Failure: Get Non-existent ===")
    response = await client.get("/materials/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_non_existent(client: httpx.AsyncClient):
    print("\n=== Testing Failure: Update Non-existent ===")
    response = await client.patch("/materials/999999", json={"price": 5000})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_non_existent(client: httpx.AsyncClient):
    print("\n=== Testing Failure: Delete Non-existent ===")
    response = await client.delete("/materials/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pagination_empty_result(client: httpx.AsyncClient):
    print("\n=== Testing Edge Case: Pagination Empty Result ===")
    response = await client.get("/materials?cursor=999999&limit=10")
    assert response.status_code == 200
    assert len(response.json()["result"]) == 0


@pytest.mark.asyncio
async def test_filter_no_matches(client: httpx.AsyncClient):
    print("\n=== Testing Edge Case: Filter No Matches ===")
    response = await client.get("/materials?category=NonExistent")
    assert response.status_code == 200
    assert len(response.json()["result"]) == 0


@pytest.mark.asyncio
async def test_cursor_pagination_flow(client: httpx.AsyncClient):
    print("\n=== Testing Cursor Pagination Flow ===")
    # Create materials to ensure we have data
    await client.post(
        "/materials/manual",
        json={
            "user_id": "test_user",
            "name": "Bread",
            "price": 2000,
            "category": "Bakery",
            "purchased_at": "2023-10-27T10:00:00",
            "expired_at": "2023-11-05T10:00:00",
            "quantity": 1,
        },
    )
    await client.post(
        "/materials/manual",
        json={
            "user_id": "test_user",
            "name": "Butter",
            "price": 5000,
            "category": "Dairy",
            "purchased_at": "2023-10-27T10:00:00",
            "expired_at": "2023-11-05T10:00:00",
            "quantity": 1,
        },
    )

    # Get first page with limit 1
    response = await client.get("/materials?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["result"]) == 1
    assert data["has_next"] is True
    next_cursor = data["next_cursor"]
    assert next_cursor is not None

    # Get next page
    response = await client.get(f"/materials?cursor={next_cursor}&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["result"]) >= 1
