from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Dict
from app.modules.forms.schemas.form import FormCreate, FormRead
from app.modules.forms.dependencies.dependencies import get_db_session, get_form_service
from app.modules.forms.services.form_service import FormService

router = APIRouter(tags=["Forms"])

@router.get("/sampleapi", status_code=status.HTTP_200_OK)
async def sampleapi(db: AsyncSession = Depends(get_db_session), service: FormService = Depends(get_form_service)):
    return "Hi Sir"

@router.post("/", response_model=FormRead, status_code=status.HTTP_201_CREATED)
async def create_form(
    data: FormCreate,
    db: AsyncSession = Depends(get_db_session),
    service: FormService = Depends(get_form_service),
):
    """
    Create a new form with fields.
    """
    return await service.create_form(db, data)

@router.get("/{form_id}", response_model=FormRead)
async def get_form(
    form_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: FormService = Depends(get_form_service),
):
    """
    Get a form by ID.
    """
    form = await service.get_form(db, str(form_id))
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form

@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_form(
    form_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: FormService = Depends(get_form_service),
):
    """
    Soft delete a form.
    """
    success = await service.soft_delete_form(db, str(form_id))
    if not success:
        raise HTTPException(status_code=404, detail="Form not found")
    return
