from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from contextvars import ContextVar
from datetime import datetime
from typing import Any
from app.core.database.db_connect.database import AsyncSessionLocal
from sqlalchemy import String, event, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# ContextVar to hold current user's email (set per-request in FastAPI middleware)
current_user_email: ContextVar[str | None] = ContextVar("current_user_email", default=None)


class AuditMixin:
    """Mixin for automatic audit columns (created/updated by & at)."""

    created_at: Mapped[datetime] = mapped_column(
                server_default=func.now(),
        nullable=False,
        # For timezone-aware: use func.now() with timezone-enabled column type if needed
    )
    created_by: Mapped[str | None] = mapped_column(
        String(255),  # or use your user.email length
        nullable=True,
        index=True,   # useful for querying "all records created by X"
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    updated_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )


class Base(DeclarativeBase, AuditMixin):
    """All models should inherit from this."""
    pass


# ─── Auto-populate user fields via events ───────────────────────────────────

@event.listens_for(Base, "before_insert", propagate=True)
def populate_created_by(mapper, connection, target):
    email = current_user_email.get()
    if email:
        target.created_by = email
        target.updated_by = email  # on create, usually same


@event.listens_for(Base, "before_update", propagate=True)
def populate_updated_by(mapper, connection, target):
    email = current_user_email.get()
    if email:
        target.updated_by = email
        # updated_at is auto-handled by onupdate=func.now()