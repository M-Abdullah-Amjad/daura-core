from typing import Optional, List, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.forms.repository.form_repository import FormFieldRepository
from app.modules.forms.models.formfields import FormField
from app.modules.forms.schemas.form_field import FormFieldCreate, FormFieldUpdate


class FormFieldService:
    """
    Service layer for FormField operations.
    Handles all business logic related to form fields.
    """
    
    def __init__(self, repository: FormFieldRepository):
        self.repository = repository

    async def create_field(
        self, 
        db: AsyncSession, 
        form_id: UUID, 
        data: FormFieldCreate,
        created_by: Optional[str] = None
    ) -> FormField:
        """
        Create a single form field.
        
        Args:
            db: Database session
            form_id: UUID of the parent form
            data: FormFieldCreate schema
            created_by: Email of the user creating the field
            
        Returns:
            Created FormField entity
        """
        field = FormField(**data.model_dump(), form_id=form_id, is_deleted=False)
        
        if created_by:
            field.created_by = created_by
            field.updated_by = created_by
            
        db.add(field)
        await db.commit()
        await db.refresh(field)
        return field

    async def get_field(
        self, 
        db: AsyncSession, 
        field_id: UUID,
        include_deleted: bool = False
    ) -> Optional[FormField]:
        """
        Get a single field by ID.
        
        Args:
            db: Database session
            field_id: UUID of the field
            include_deleted: Whether to include soft-deleted fields
            
        Returns:
            FormField if found, None otherwise
        """
        stmt = select(FormField).where(FormField.id == field_id)
        
        if not include_deleted:
            stmt = stmt.where(FormField.is_deleted == False)
            
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_fields_by_form(
        self, 
        db: AsyncSession, 
        form_id: UUID,
        include_deleted: bool = False
    ) -> List[FormField]:
        """
        Get all fields for a specific form.
        
        Args:
            db: Database session
            form_id: UUID of the form
            include_deleted: Whether to include soft-deleted fields
            
        Returns:
            List of FormField entities sorted by position
        """
        stmt = select(FormField).where(FormField.form_id == form_id)
        
        if not include_deleted:
            stmt = stmt.where(FormField.is_deleted == False)
            
        stmt = stmt.order_by(FormField.position)
        
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_field(
        self, 
        db: AsyncSession, 
        field_id: UUID, 
        data: FormFieldUpdate,
        updated_by: Optional[str] = None
    ) -> Optional[FormField]:
        """
        Update a form field.
        
        Args:
            db: Database session
            field_id: UUID of the field to update
            data: FormFieldUpdate schema
            updated_by: Email of the user updating the field
            
        Returns:
            Updated FormField if found, None otherwise
        """
        field = await self.get_field(db, field_id)
        
        if not field:
            return None
            
        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(field, key, value)
            
        if updated_by:
            field.updated_by = updated_by
            
        db.add(field)
        await db.commit()
        await db.refresh(field)
        return field

    async def soft_delete_field(
        self, 
        db: AsyncSession, 
        field_id: UUID,
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Soft delete a form field.
        
        Args:
            db: Database session
            field_id: UUID of the field to delete
            deleted_by: Email of the user deleting the field
            
        Returns:
            True if field was deleted, False if not found or already deleted
        """
        field = await self.get_field(db, field_id)
        
        if not field:
            return False
            
        field.is_deleted = True
        
        if deleted_by:
            field.updated_by = deleted_by
            
        db.add(field)
        await db.commit()
        return True

    async def reorder_fields(
        self, 
        db: AsyncSession, 
        form_id: UUID, 
        field_positions: Dict[str, int],
        updated_by: Optional[str] = None
    ) -> bool:
        """
        Reorder fields in a form.
        
        Args:
            db: Database session
            form_id: UUID of the form
            field_positions: Dict mapping field_id (str) to new position (int)
            updated_by: Email of the user reordering fields
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If form not found or field doesn't belong to form
        """
        # Get all fields for this form
        fields = await self.get_fields_by_form(db, form_id, include_deleted=False)
        
        if not fields:
            raise ValueError("Form has no fields or form not found")
            
        # Create a map of field IDs for validation
        field_map = {str(field.id): field for field in fields}
        
        # Update positions
        for field_id_str, new_position in field_positions.items():
            if field_id_str not in field_map:
                raise ValueError(f"Field {field_id_str} does not belong to form {form_id}")
                
            field = field_map[field_id_str]
            field.position = new_position
            
            if updated_by:
                field.updated_by = updated_by
                
            db.add(field)
            
        await db.commit()
        return True