import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import status
from app.api.materials import (
    get_materials,
    create_material,
    get_material,
    update_material,
    delete_material,
)
from app.models import Material, MaterialCreate, MaterialUpdate, Pagination
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_get_materials_empty():
    session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    session.execute.return_value = mock_result

    result = await get_materials(session=session)

    assert isinstance(result, Pagination)
    assert result.result == []
    assert result.has_next is False
    assert result.next_cursor is None


@pytest.mark.asyncio
async def test_create_material():
    session = AsyncMock()
    material_in = MaterialCreate(
        user_id="test_user",
        name="Test Item",
        price=1000,
        category="Test",
        purchased_at=datetime.now(timezone.utc),
        expired_at=datetime.now(timezone.utc),
        quantity=10,
    )

    result = await create_material(material=material_in, session=session)

    assert result.name == "Test Item"
    assert result.user_id == "test_user"
    session.add.assert_called_once()
    await session.commit()
    await session.refresh(result)


@pytest.mark.asyncio
async def test_get_material_found():
    session = AsyncMock()
    mock_material = Material(
        id=1,
        user_id="test_user",
        name="Test",
        price=100,
        category="Test",
        purchased_at=datetime.now(timezone.utc),
        expired_at=datetime.now(timezone.utc),
        quantity=1,
    )
    session.get.return_value = mock_material

    result = await get_material(id=1, session=session)
    assert result == mock_material


@pytest.mark.asyncio
async def test_get_material_not_found():
    session = AsyncMock()
    session.get.return_value = None

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await get_material(id=999, session=session)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_material():
    session = AsyncMock()
    mock_material = Material(
        id=1,
        user_id="test_user",
        name="Old",
        price=100,
        category="Test",
        purchased_at=datetime.now(timezone.utc),
        expired_at=datetime.now(timezone.utc),
        quantity=1,
    )
    session.get.return_value = mock_material

    update_data = MaterialUpdate(name="New")
    result = await update_material(id=1, material_update=update_data, session=session)

    assert result.name == "New"
    await session.add(mock_material)
    await session.commit()
    await session.refresh(mock_material)


@pytest.mark.asyncio
async def test_delete_material():
    session = AsyncMock()
    mock_material = Material(
        id=1,
        user_id="test_user",
        name="Test",
        price=100,
        category="Test",
        purchased_at=datetime.now(timezone.utc),
        expired_at=datetime.now(timezone.utc),
        quantity=1,
    )
    session.get.return_value = mock_material

    await delete_material(id=1, session=session)

    session.delete.assert_called_once_with(mock_material)
    await session.commit()
