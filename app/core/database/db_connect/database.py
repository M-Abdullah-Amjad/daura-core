# db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextvars import ContextVar
from datetime import datetime
from typing import Any
from app.core.config import settings

from sqlalchemy import String, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Construct DATABASE_URL from individual settings
DATABASE_URL = (
    f"{settings.DB_DRIVER}://"
    f"{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/"
    f"{settings.DB_NAME}"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # set False in production
)

# Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session