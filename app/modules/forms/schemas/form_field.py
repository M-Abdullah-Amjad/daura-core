from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from .base import AuditBase

class FormFieldBase(BaseModel):
    label: str
    field_type: str
    required: str = "false"
    position: int = 0

class FormFieldCreate(FormFieldBase):
    pass
    # form_id is typically handled by the parent Form or passed in context

class FormFieldUpdate(BaseModel):
    label: Optional[str] = None
    field_type: Optional[str] = None
    required: Optional[str] = None
    position: Optional[int] = None

class FormFieldRead(FormFieldBase, AuditBase):
    form_id: UUID
