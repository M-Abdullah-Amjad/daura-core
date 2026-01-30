from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.modules.forms.repository.form_submission_repository import FormSubmissionRepository
from app.modules.forms.models.formsubmission import FormSubmission
from app.modules.forms.models.form import Form
from app.modules.forms.schemas.form_submission import FormSubmissionCreate, FormSubmissionUpdate


class FormSubmissionService:
    """
    Service layer for FormSubmission operations.
    Handles form submissions with automatic snapshot preservation.
    """
    
    def __init__(self, repository: FormSubmissionRepository, form_service):
        """
        Initialize FormSubmissionService.
        
        Args:
            repository: FormSubmissionRepository instance
            form_service: FormService instance (for fetching form structure)
        """
        self.repository = repository
        self.form_service = form_service

    async def create_submission(
        self, 
        db: AsyncSession, 
        form_id: UUID,
        data: Dict[str, Any],
        created_by: Optional[str] = None
    ) -> FormSubmission:
        """
        Create a new form submission with automatic snapshot.
        
        This method:
        1. Validates the form exists
        2. Fetches current form structure (fields)
        3. Stores submission data + form snapshot
        4. Ensures historical data preservation
        
        Args:
            db: Database session
            form_id: UUID of the form being submitted
            data: Dictionary of field values (key=field_label, value=user_input)
            created_by: Email of the user submitting the form
            
        Returns:
            Created FormSubmission entity
            
        Raises:
            ValueError: If form not found or deleted
        """
        # 1. Validate form exists and is not deleted
        form = await self.form_service.get_form(db, str(form_id))
        
        if not form:
            raise ValueError(f"Form {form_id} not found or has been deleted")
        
        # 2. Create snapshot of current form structure
        form_snapshot = {
            "form_id": str(form.id),
            "form_name": form.name,
            "form_description": form.description,
            "fields": [
                {
                    "id": str(field.id),
                    "label": field.label,
                    "field_type": field.field_type,
                    "required": field.required,
                    "position": field.position
                }
                for field in form.fields
                if not field.is_deleted  # Only include active fields
            ],
            "snapshot_timestamp": form.updated_at.isoformat() if hasattr(form, 'updated_at') else None
        }
        
        # 3. Create submission
        submission = FormSubmission(
            form_id=form_id,
            data=data,
            form_snapshot=form_snapshot
        )
        
        if created_by:
            submission.created_by = created_by
            submission.updated_by = created_by
        
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        
        return submission

    async def get_submission(
        self, 
        db: AsyncSession, 
        submission_id: UUID
    ) -> Optional[FormSubmission]:
        """
        Get a single submission by ID.
        
        Args:
            db: Database session
            submission_id: UUID of the submission
            
        Returns:
            FormSubmission if found, None otherwise
        """
        stmt = select(FormSubmission).where(FormSubmission.id == submission_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_submissions_by_form(
        self, 
        db: AsyncSession, 
        form_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[FormSubmission]:
        """
        Get all submissions for a specific form.
        
        Args:
            db: Database session
            form_id: UUID of the form
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of FormSubmission entities ordered by creation date (newest first)
        """
        stmt = (
            select(FormSubmission)
            .where(FormSubmission.form_id == form_id)
            .order_by(FormSubmission.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_submission(
        self, 
        db: AsyncSession, 
        submission_id: UUID, 
        data: Dict[str, Any],
        updated_by: Optional[str] = None
    ) -> Optional[FormSubmission]:
        """
        Update an existing submission's data.
        
        NOTE: This updates the submission data but does NOT update the snapshot.
        The snapshot remains frozen to the original submission time.
        
        Args:
            db: Database session
            submission_id: UUID of the submission to update
            data: New data dictionary
            updated_by: Email of the user updating the submission
            
        Returns:
            Updated FormSubmission if found, None otherwise
        """
        submission = await self.get_submission(db, submission_id)
        
        if not submission:
            return None
        
        # Update data only (snapshot remains unchanged)
        submission.data = data
        
        if updated_by:
            submission.updated_by = updated_by
        
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        
        return submission

    async def delete_submission(
        self, 
        db: AsyncSession, 
        submission_id: UUID
    ) -> bool:
        """
        Hard delete a submission.
        
        NOTE: This is a HARD delete, not soft delete.
        Use with caution - deleted submissions cannot be recovered.
        
        Args:
            db: Database session
            submission_id: UUID of the submission to delete
            
        Returns:
            True if submission was deleted, False if not found
        """
        submission = await self.get_submission(db, submission_id)
        
        if not submission:
            return False
        
        await db.delete(submission)
        await db.commit()
        return True

    async def get_submission_count(
        self, 
        db: AsyncSession, 
        form_id: UUID
    ) -> int:
        """
        Get total count of submissions for a form.
        
        Args:
            db: Database session
            form_id: UUID of the form
            
        Returns:
            Total number of submissions
        """
        from sqlalchemy import func
        
        stmt = select(func.count(FormSubmission.id)).where(FormSubmission.form_id == form_id)
        result = await db.execute(stmt)
        return result.scalar() or 0
