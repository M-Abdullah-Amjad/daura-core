from app.core.database.repositories.baserepo import BaseRepository
from modules.forms.models.formfields import FormField
class FormFieldRepository(BaseRepository):
    def __init__(self, FormField):
        super().__init__(FormField)