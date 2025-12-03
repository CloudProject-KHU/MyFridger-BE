from typing import List, Optional
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func

from app.core.db import get_session
from app.models import (
    Material,
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    Pagination,
)
from app.core.config import settings
from app.services.materials import extract_items_from_ocr

router = APIRouter()


@router.get("", response_model=Pagination[MaterialResponse])
async def get_materials(
    category: Optional[str] = None,
    search: Optional[str] = None,
    cursor: Optional[str] = None,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    query = select(Material)

    if category:
        query = query.where(Material.category == category)
    if search:
        query = query.where(Material.name.contains(search))
    if cursor:
        query = query.where(Material.id > int(cursor))

    query = query.order_by(Material.id).limit(limit + 1)

    result = await session.execute(query)
    materials = result.scalars().all()

    has_next = False
    next_cursor = None

    if len(materials) > limit:
        has_next = True
        materials = materials[:limit]
        next_cursor = str(materials[-1].id)

    return Pagination[MaterialResponse](
        result=materials, next_cursor=next_cursor, has_next=has_next, size=limit
    )


@router.get("/{id}", response_model=MaterialResponse)
async def get_material(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    material = await session.get(Material, id)
    if not material:
        raise HTTPException(status_code=404, detail="재료를 찾을 수 없습니다.")
    return material


@router.post(
    "/receipt",
    response_model=List[MaterialResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_materials_from_receipt(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    content = await file.read()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.ocr.space/parse/image",
            files={"file": (file.filename, content, file.content_type)},
            data={
                "apikey": settings.OCR_API_KEY,
                "language": "kor",
                "detectOrientation": "true",
                "isTable": "true",
                "OCREngine": "2",
            },
        )

    result = response.json()

    data = ""
    for threshold in [5, 10, 15, 20]:
        if isinstance(data, list) and len(data) > 0:
            break
        data = extract_items_from_ocr(result, 10, threshold)

    if isinstance(data, str):
        raise HTTPException(status_code=400, detail=data)

    materials = []
    for item in data:
        print(item)
        material = Material(
            name=item["name"],
            price=item["price"],
            quantity=item["quantity"],
            currency="KRW",
            category="기타",
            purchased_at=func.now(),
            expired_at=func.now(),
        )
        materials.append(material)

    for material in materials:
        session.add(material)

    if materials:
        await session.commit()
        for material in materials:
            await session.refresh(material)

    return materials


@router.post(
    "/manual", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED
)
async def create_material(
    material: MaterialCreate,
    session: AsyncSession = Depends(get_session),
):
    db_material = Material.model_validate(material)
    session.add(db_material)
    await session.commit()
    await session.refresh(db_material)
    return db_material


@router.patch("/{id}", response_model=MaterialResponse)
async def update_material(
    id: int,
    material_update: MaterialUpdate,
    session: AsyncSession = Depends(get_session),
):
    db_material = await session.get(Material, id)
    if not db_material:
        raise HTTPException(status_code=404, detail="재료를 찾을 수 없습니다.")

    material_data = material_update.model_dump(exclude_unset=True)
    for key, value in material_data.items():
        setattr(db_material, key, value)

    session.add(db_material)
    await session.commit()
    await session.refresh(db_material)
    return db_material


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    db_material = await session.get(Material, id)
    if not db_material:
        raise HTTPException(status_code=404, detail="재료를 찾을 수 없습니다.")

    await session.delete(db_material)
    await session.commit()


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def bulk_delete_materials(
    id: List[int] = Query(...),
    session: AsyncSession = Depends(get_session),
):
    statement = delete(Material).where(Material.id.in_(id))
    await session.execute(statement)
    await session.commit()
