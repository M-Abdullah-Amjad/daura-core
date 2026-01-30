from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.modules.forms.schemas.form_submission import (
    FormSubmissionCreate, 
    FormSubmissionRead,
    FormSubmissionUpdate
)
from app.modules.forms.dependencies.dependencies import (
    get_db_session, 
    get_form_submission_service
)
from app.modules.forms.services.form_submission_service import FormSubmissionService

router = APIRouter(tags=["Form Submissions"])


@router.post("/{form_id}/submissions", response_model=FormSubmissionRead, status_code=status.HTTP_201_CREATED)
async def create_submission(
    form_id: UUID,
    submission_data: FormSubmissionCreate,
    db: AsyncSession = Depends(get_db_session),
    service: FormSubmissionService = Depends(get_form_submission_service),
):
    """
    Submit a form with data.
    
    Automatically creates a snapshot of the form structure to preserve
    historical data even if fields are later deleted.
    
    Args:
        form_id: UUID of the form being submitted
        submission_data: Contains 'data' (key-value pairs) and optional 'form_id'
        
    Example Request Body:
    {
        "form_id": "form-uuid",
        "data": {
            "donor_name": "John Doe",
            "amount": 150,
            "email": "john@example.com"
        }
    }
    
    Returns:
        Created submission with snapshot
    """
    try:
        # Note: submission_data includes form_id, but we use path param for consistency
        submission = await service.create_submission(
            db=db,
            form_id=form_id,
            data=submission_data.data
        )
        return submission
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{form_id}/submissions", response_model=List[FormSubmissionRead])
async def get_form_submissions(
    form_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    service: FormSubmissionService = Depends(get_form_submission_service),
):
    """
    Get all submissions for a specific form.
    
    Args:
        form_id: UUID of the form
        skip: Number of records to skip (pagination)
        limit: Maximum records to return (default 100, max 100)
        
    Returns:
        List of submissions ordered by creation date (newest first)
    """
    # Enforce max limit
    limit = min(limit, 100)
    
    submissions = await service.get_submissions_by_form(db, form_id, skip, limit)
    return submissions


@router.get("/submissions/{submission_id}", response_model=FormSubmissionRead)
async def get_submission(
    submission_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: FormSubmissionService = Depends(get_form_submission_service),
):
    """
    Get a specific submission by ID.
    
    Args:
        submission_id: UUID of the submission
        
    Returns:
        Submission with data and form_snapshot
    """
    submission = await service.get_submission(db, submission_id)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return submission


@router.put("/submissions/{submission_id}", response_model=FormSubmissionRead)
async def update_submission(
    submission_id: UUID,
    update_data: FormSubmissionUpdate,
    db: AsyncSession = Depends(get_db_session),
    service: FormSubmissionService = Depends(get_form_submission_service),
):
    """
    Update a submission's data.
    
    NOTE: This updates the submission data but does NOT update the snapshot.
    The snapshot remains frozen to preserve historical accuracy.
    
    Args:
        submission_id: UUID of the submission to update
        update_data: New data dictionary
        
    Returns:
        Updated submission
    """
    if not update_data.data:
        raise HTTPException(status_code=400, detail="No data provided for update")
    
    submission = await service.update_submission(db, submission_id, update_data.data)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return submission


@router.delete("/submissions/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_submission(
    submission_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: FormSubmissionService = Depends(get_form_submission_service),
):
    """
    Delete a submission (HARD DELETE).
    
    WARNING: This permanently deletes the submission and cannot be undone.
    Use with caution.
    
    Args:
        submission_id: UUID of the submission to delete
    """
    success = await service.delete_submission(db, submission_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return


@router.get("/{form_id}/submissions/count")
async def get_submission_count(
    form_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: FormSubmissionService = Depends(get_form_submission_service),
):
    """
    Get total count of submissions for a form.
    
    Args:
        form_id: UUID of the form
        
    Returns:
        {"count": <number>}
    """
    count = await service.get_submission_count(db, form_id)
    return {"count": count}
