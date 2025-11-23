from fastapi import APIRouter
from api import materials

api_router = APIRouter()

api_router.include_router(materials.router, prefix="/materials", tags=["Materials"])
