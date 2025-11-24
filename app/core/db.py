import ssl
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import settings

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"ssl": ssl_context} if settings.ENVIRONMENT == "production" else {},
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
