# models/form.py
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    UUID,
    Integer,
    String,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship,Mapped
from sqlalchemy.sql import func
from app.core.database.models.basemodel import Base,mapped_column

if TYPE_CHECKING:
    from app.modules.forms.models.form import Form

class FormField(Base):
    __tablename__ = "form_fields"

    id : Mapped[UUID]= mapped_column(UUID, primary_key=True, default=uuid4)
    form_id:   Mapped[UUID]= mapped_column(ForeignKey("forms.id", ondelete="CASCADE"))

    label:   Mapped[String]= mapped_column(String(255), nullable=False)
    field_type:   Mapped[String]= mapped_column(String(50), nullable=False)  # text, number, email, select
    required:   Mapped[String]= mapped_column(String(10), default="false")
    position: Mapped[Integer] = mapped_column(Integer, default=0)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    form: Mapped["Form"] = relationship("Form", back_populates="fields")

    def __repr__(self):
        return f"<FormField {self.label} ({self.field_type})>"
