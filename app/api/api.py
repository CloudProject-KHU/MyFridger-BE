from fastapi import APIRouter
from app.api import materials

api_router = APIRouter()

api_router.include_router(materials.router, prefix="/materials", tags=["Materials"])
api_router.include_router(recipes.router, prefix="/recipes", tags=["Recipes"])
api_router.include_router(recommends.router, prefix="/recommends", tags=["Recommends"])