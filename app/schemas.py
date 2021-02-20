from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, SecretStr, validator

from app import config
from app.utils import get_file_url


class UserModel(BaseModel):
    id: UUID = ...
    email: str = ...
    nickname: str = ""
    password_hash = SecretStr
    photo: str = None
    is_admin: bool = False

    class Config:
        orm_mode = True

    @validator("photo", pre=True, always=True)
    def get_photo(cls, v, *, values, **kwargs):
        return get_file_url(v, file_host=config.MEDIA_URL)


class TranslationModel(BaseModel):
    id: int
    translation: str
    line_id: int
    translator_id: UUID
    created_at: datetime
    updated_at: datetime
