from app.core.database.repositories.baserepo import BaseRepository
from app.modules.forms.models.formfields import FormField
from app.modules.forms.schemas.form_field import FormFieldCreate, FormFieldUpdate

class FormFieldRepository(BaseRepository[FormField, FormFieldCreate, FormFieldUpdate]):
    def __init__(self):
        super().__init__(FormField)

class FormRepository(BaseRepository):
    def __init__(self, entity):
        super().__init__(entity)

class FormSubmissionRepository(BaseRepository):
    def __init__(self, FormSubmission):
        super().__init__(FormSubmission)