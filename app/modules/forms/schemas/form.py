from typing import List, Optional
from pydantic import BaseModel
from .base import AuditBase
from .form_field import FormFieldCreate, FormFieldRead

class FormBase(BaseModel):
    name: str
    description: Optional[str] = None

class FormCreate(FormBase):
    fields: Optional[List[FormFieldCreate]] = []

class FormUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[FormFieldCreate]] = None

class FormRead(FormBase, AuditBase):
    fields: List[FormFieldRead] = []
    # submissions relationship is deliberately omitted to prevent fetching all submissions with the form
