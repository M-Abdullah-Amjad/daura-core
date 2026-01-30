# app/repositories/base_repository.py
from typing import Generic, TypeVar, Type, Any, Optional, List, Sequence
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.models.basemodel import Base

T = TypeVar("T", bound=Base)
CreateDTO = TypeVar("CreateDTO")
UpdateDTO = TypeVar("UpdateDTO")


class BaseRepository(Generic[T, CreateDTO, UpdateDTO]):
    """
    Generic repository similar to NestJS/TypeORM base repository.
    Extend this for every entity.
    """

    def __init__(self, entity: Type[T]):
        self.entity = entity

    async def create(
        self,
        db: AsyncSession,
        dto: CreateDTO,
        created_by: Optional[str] = None,
    ) -> T:
        data = dto.model_dump(exclude_unset=True)
        entity = self.entity(**data)

        if hasattr(entity, "created_by") and created_by:
            entity.created_by = created_by
        if hasattr(entity, "updated_by") and created_by:
            entity.updated_by = created_by

        db.add(entity)
        await db.commit()
        await db.refresh(entity)
        return entity

    async def find_one_by_id(self, db: AsyncSession, id: UUID | int) -> Optional[T]:
        stmt = select(self.entity).where(self.entity.id == id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_one_or_fail(self, db: AsyncSession, id: UUID | int) -> T:
        entity = await self.find_one_by_id(db, id)
        if not entity:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.entity.__name__} not found")
        return entity

    async def find_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Sequence] = None,
    ) -> List[T]:
        stmt = select(self.entity).offset(skip).limit(limit)
        if filters:
            stmt = stmt.where(*filters)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        entity: T,
        dto: UpdateDTO,
        updated_by: Optional[str] = None,
    ) -> T:
        data = dto.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(entity, key, value)

        if hasattr(entity, "updated_by") and updated_by is not None:
            entity.updated_by = updated_by

        db.add(entity)
        await db.commit()
        await db.refresh(entity)
        return entity

    async def delete(self, db: AsyncSession, id: UUID | int) -> bool:
        stmt = delete(self.entity).where(self.entity.id == id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0