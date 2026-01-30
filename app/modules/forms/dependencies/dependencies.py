from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.db_connect.database import get_db
from app.modules.auth.dependencies.dependencies import get_current_user

# Dependency to get database session
async def get_db_session() -> AsyncSession:
    async for session in get_db():
        yield session

# Dependency to get current user (requires authentication)
async def get_authenticated_user(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return current_user

from app.modules.forms.repository.form_repository import FormRepository, FormFieldRepository
from app.modules.forms.models.form import Form
from app.modules.forms.services.form_service import FormService
from app.modules.forms.services.form_field_service import FormFieldService

async def get_form_field_service() -> FormFieldService:
    """
    Dependency to get FormFieldService instance.
    
    Returns:
        FormFieldService instance with repository
    """
    repository = FormFieldRepository()
    return FormFieldService(repository)

async def get_form_service(
    field_service: FormFieldService = Depends(get_form_field_service)
) -> FormService:
    """
    Dependency to get FormService instance.
    Injects FormFieldService for field operations.
    
    Args:
        field_service: Injected FormFieldService instance
        
    Returns:
        FormService instance with repository and field service
    """
    repository = FormRepository(Form)
    return FormService(repository, field_service)

from app.modules.forms.repository.form_submission_repository import FormSubmissionRepository
from app.modules.forms.services.form_submission_service import FormSubmissionService

async def get_form_submission_service(
    form_service: FormService = Depends(get_form_service)
) -> FormSubmissionService:
    """
    Dependency to get FormSubmissionService instance.
    Injects FormService for form validation and snapshot creation.
    
    Args:
        form_service: Injected FormService instance
        
    Returns:
        FormSubmissionService instance with repository and form service
    """
    repository = FormSubmissionRepository()
    return FormSubmissionService(repository, form_service)