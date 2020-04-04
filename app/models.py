from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, SecretStr, validator

from app import config


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
        if not v or v.startswith("http"):
            return v
        else:
            return f"{config.MEDIA_URL}/{v}"


class AuthModel(BaseModel):
    is_new: bool
    access_token: str
    refresh_token: str
    user: UserModel


class TranslationModel(BaseModel):
    id: int
    translation: str
    line_id: int
    translator_id: UUID
    created_at: datetime
    updated_at: datetime