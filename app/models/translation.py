from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class TranslationModel(BaseModel):

    id: int
    translation: str
    line_id: int
    translator_id: UUID
    created_at: datetime
    updated_at: datetime
