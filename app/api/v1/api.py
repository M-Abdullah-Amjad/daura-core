from fastapi import APIRouter
from app.api.v1.routes import protected
from app.modules.auth.routers.router import router as auth_router
from app.modules.forms.routers.form_router import router as form_router
from app.modules.forms.routers.form_field_router import router as form_field_router
from app.modules.forms.routers.form_submission_router import router as form_submission_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(form_router, prefix="/forms", tags=["Forms"])
api_router.include_router(form_field_router, prefix="/forms", tags=["Form Fields"])
api_router.include_router(form_submission_router, prefix="/forms", tags=["Form Submissions"])
api_router.include_router(protected.router)