from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.forms.schemas.form import FormCreate, FormRead
from app.modules.forms.repository.form_repository import FormRepository
from app.modules.forms.models.form import Form
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional


class FormService:
    """
    Service layer for Form operations.
    Delegates field-related operations to FormFieldService.
    """
    
    def __init__(self, repository: FormRepository, field_service):
        """
        Initialize FormService with repository and field service.
        
        Args:
            repository: FormRepository instance
            field_service: FormFieldService instance (injected for field operations)
        """
        self.repository = repository
        self.field_service = field_service

    async def create_form(
        self, 
        db: AsyncSession, 
        data: FormCreate,
        created_by: Optional[str] = None
    ) -> FormRead:
        """
        Create a new form with the provided data.
        Delegates field creation to FormFieldService.
        
        Args:
            db: Database session
            data: FormCreate schema
            created_by: Email of the user creating the form
            
        Returns:
            Created Form entity with fields
        """
        # Create the form entity (without fields)
        form_data = data.model_dump(exclude={"fields"})
        form_data["is_deleted"] = False
        
        form = Form(**form_data)
        
        if created_by:
            form.created_by = created_by
            form.updated_by = created_by
            
        db.add(form)
        await db.flush()  # Get form ID
        
        # Delegate field creation to FormFieldService
        if data.fields:
            for i, field_data in enumerate(data.fields):
                # Ensure position is set
                if not hasattr(field_data, 'position') or field_data.position is None:
                    field_data.position = i
                    
                await self.field_service.create_field(
                    db=db, 
                    form_id=form.id, 
                    data=field_data,
                    created_by=created_by
                )
        
        await db.commit()
        await db.refresh(form)
        
        # Load fields relationship
        form = await self.get_form(db, str(form.id))
        return form

    async def get_form(
        self, 
        db: AsyncSession, 
        form_id: str
    ) -> Optional[FormRead]:
        """
        Get a form by ID, excluding deleted ones.
        
        Args:
            db: Database session
            form_id: UUID of the form (as string)
            
        Returns:
            Form with non-deleted fields sorted by position, or None if not found
        """
        stmt = (
            select(Form)
            .where(Form.id == form_id)
            .where(Form.is_deleted == False)
            .options(selectinload(Form.fields))  # Load fields relationship
        )
        
        result = await db.execute(stmt)
        form = result.scalar_one_or_none()
        
        if not form:
            return None
            
        # Filter deleted fields and sort by position
        form.fields = sorted(
            [f for f in form.fields if not f.is_deleted], 
            key=lambda x: x.position
        )
        
        return form

    async def soft_delete_form(
        self, 
        db: AsyncSession, 
        form_id: str,
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Soft delete a form.
        Note: This does NOT delete associated fields (independent lifecycle).
        
        Args:
            db: Database session
            form_id: UUID of the form (as string)
            deleted_by: Email of the user deleting the form
            
        Returns:
            True if form was deleted, False if not found or already deleted
        """
        form = await self.repository.find_one_by_id(db, form_id)
        
        if not form or form.is_deleted:
            return False
            
        form.is_deleted = True
        
        if deleted_by:
            form.updated_by = deleted_by
            
        await db.commit()
        return True
        
    async def samplapi(self):
        """Sample API endpoint for testing."""
        return "sample api"