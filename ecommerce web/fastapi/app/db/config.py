# app/db/config.py
from typing import AsyncGenerator, Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# -------------------------
# Use DATABASE_URL from Pydantic Settings
# -------------------------
DATABASE_URL = settings.DATABASE_URL

# -------------------------
# Async Engine
# -------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=True,       # Set to False in production
    future=True
)

# -------------------------
# Async Session
# -------------------------
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# -------------------------
# Dependency for FastAPI routes
# -------------------------
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
