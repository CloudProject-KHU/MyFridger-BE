from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.db import engine
from app.api import api_router

from app.models import SQLModel
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield


app = FastAPI(
    title="MyFridger API",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.include_router(api_router)
