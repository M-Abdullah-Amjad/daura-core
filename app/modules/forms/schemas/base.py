from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class AuditBase(BaseModel):
    """Base schema for read models including ID and audit timestamps."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
