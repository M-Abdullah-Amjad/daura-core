from typing import Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel
from .base import AuditBase

class FormSubmissionBase(BaseModel):
    data: Dict[str, Any]

class FormSubmissionCreate(FormSubmissionBase):
    form_id: UUID
    form_snapshot: Optional[Dict[str, Any]] = None  # Snapshot of form structure at submission time

class FormSubmissionUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None

class FormSubmissionRead(FormSubmissionBase, AuditBase):
    form_id: UUID
    form_snapshot: Optional[Dict[str, Any]] = None  # Historical form structure
