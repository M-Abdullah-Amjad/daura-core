from app.core.database.repositories.baserepo import BaseRepository
from app.modules.forms.models.formsubmission import FormSubmission
from app.modules.forms.schemas.form_submission import FormSubmissionCreate, FormSubmissionUpdate

class FormSubmissionRepository(BaseRepository[FormSubmission, FormSubmissionCreate, FormSubmissionUpdate]):
    def __init__(self):
        super().__init__(FormSubmission)