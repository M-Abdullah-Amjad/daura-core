from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Dict, List
from app.modules.forms.schemas.form_field import FormFieldCreate, FormFieldRead, FormFieldUpdate
from app.modules.forms.dependencies.dependencies import get_db_session, get_form_field_service
from app.modules.forms.services.form_field_service import FormFieldService

router = APIRouter(tags=["Form Fields"])


@router.post("/{form_id}/fields", response_model=FormFieldRead, status_code=status.HTTP_201_CREATED)
async def create_field(
    form_id: UUID,
    data: FormFieldCreate,
    db: AsyncSession = Depends(get_db_session),
    service: FormFieldService = Depends(get_form_field_service),
):
    """
    Add a new field to an existing form.
    
    Args:
        form_id: UUID of the parent form
        data: FormFieldCreate schema
        
    Returns:
        Created FormField
    """
    field = await service.create_field(db, form_id, data)
    return field


@router.get("/{form_id}/fields", response_model=List[FormFieldRead])
async def get_form_fields(
    form_id: UUID,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db_session),
    service: FormFieldService = Depends(get_form_field_service),
):
    """
    Get all fields for a specific form.
    
    Args:
        form_id: UUID of the form
        include_deleted: Whether to include soft-deleted fields
        
    Returns:
        List of FormField entities sorted by position
    """
    fields = await service.get_fields_by_form(db, form_id, include_deleted)
    return fields


@router.put("/{form_id}/fields/reorder", status_code=status.HTTP_200_OK)
async def reorder_fields(
    form_id: UUID,
    field_positions: Dict[str, int], 
    db: AsyncSession = Depends(get_db_session),
    service: FormFieldService = Depends(get_form_field_service),
):
    """
    Reorder fields in a form.
    
    Args:
        form_id: UUID of the form
        field_positions: Dict mapping field_id (str UUID) to new position (int)
        
    Example request body:
    {
        "field-uuid-1": 0,
        "field-uuid-2": 1,
        "field-uuid-3": 2
    }
    
    Returns:
        Success message
    """
    try:
        await service.reorder_fields(db, form_id, field_positions)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Fields reordered successfully"}


@router.get("/{form_id}/fields/{field_id}", response_model=FormFieldRead)
async def get_field(
    form_id: UUID,
    field_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: FormFieldService = Depends(get_form_field_service),
):
    """
    Get a specific field by ID.
    
    Args:
        form_id: UUID of the parent form (for RESTful path)
        field_id: UUID of the field
        
    Returns:
        FormField entity
    """
    field = await service.get_field(db, field_id)
    
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
        
    # Verify field belongs to the specified form
    if str(field.form_id) != str(form_id):
        raise HTTPException(status_code=400, detail="Field does not belong to specified form")
        
    return field


@router.put("/{form_id}/fields/{field_id}", response_model=FormFieldRead)
async def update_field(
    form_id: UUID,
    field_id: UUID,
    data: FormFieldUpdate,
    db: AsyncSession = Depends(get_db_session),
    service: FormFieldService = Depends(get_form_field_service),
):
    """
    Update a form field.
    
    Args:
        form_id: UUID of the parent form (for RESTful path)
        field_id: UUID of the field to update
        data: FormFieldUpdate schema
        
    Returns:
        Updated FormField
    """
    field = await service.update_field(db, field_id, data)
    
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
        
    # Verify field belongs to the specified form
    if str(field.form_id) != str(form_id):
        raise HTTPException(status_code=400, detail="Field does not belong to specified form")
        
    return field


@router.delete("/{form_id}/fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field(
    form_id: UUID,
    field_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: FormFieldService = Depends(get_form_field_service),
):
    """
    Soft delete a form field.
    Note: This does not affect historical form submissions.
    
    Args:
        form_id: UUID of the parent form (for RESTful path)
        field_id: UUID of the field to delete
    """
    # First verify field exists and belongs to form
    field = await service.get_field(db, field_id)
    
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
        
    if str(field.form_id) != str(form_id):
        raise HTTPException(status_code=400, detail="Field does not belong to specified form")
    
    success = await service.soft_delete_field(db, field_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Field not found")
        
    return


@router.put("/{form_id}/fields/reorder", status_code=status.HTTP_200_OK)
async def reorder_fields(
    form_id: UUID,
    field_positions: Dict[str, int], 
    db: AsyncSession = Depends(get_db_session),
    service: FormFieldService = Depends(get_form_field_service),
):
    """
    Reorder fields in a form.
    
    Args:
        form_id: UUID of the form
        field_positions: Dict mapping field_id (str UUID) to new position (int)
        
    Example request body:
    {
        "field-uuid-1": 0,
        "field-uuid-2": 1,
        "field-uuid-3": 2
    }
    
    Returns:
        Success message
    """
    try:
        await service.reorder_fields(db, form_id, field_positions)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Fields reordered successfully"}
