# models/form.py
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    UUID,
    JSON,
)
from sqlalchemy.orm import relationship,mapped_column,Mapped
from app.core.database.models.basemodel import Base

if TYPE_CHECKING:
    from app.modules.forms.models.formfields import FormField
    from app.modules.forms.models.formsubmission import FormSubmission


class Form(Base):
    __tablename__ = "forms"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    name: Mapped[String] = mapped_column(String(255), nullable=False)
    description: Mapped[String] = mapped_column(String(500), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    fields: Mapped[list["FormField"]] = relationship("FormField", back_populates="form")
    submissions: Mapped[list["FormSubmission"]] = relationship("FormSubmission", back_populates="form")

    def __repr__(self):
        return f"<Form id={self.id} name={self.name}>"

