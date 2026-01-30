# models/form.py
from __future__ import annotations  # only needed if you use forward refs in < Python 3.10–3.11
from typing import Annotated, Optional
from sqlalchemy import ForeignKey, func, JSON
from uuid import UUID, uuid4
import datetime
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from app.modules.forms.models.form import Form
from app.core.database.models.basemodel import Base


# 2. Then your model (type-safe & modern)
class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id:             Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    form_id:        Mapped[UUID] = mapped_column(ForeignKey("forms.id", ondelete="CASCADE"))
    data:           Mapped[dict] = mapped_column(JSON, nullable=False)   # or use dict[str, Any]
    form_snapshot:  Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Store form structure at submission time

    # Relationships (also modern style)
    form: Mapped["Form"] = relationship(back_populates="submissions")

    def __repr__(self) -> str:
        return f"<FormSubmission id={self.id} form_id={self.form_id}>"