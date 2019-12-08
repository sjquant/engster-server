from uuid import UUID
from pydantic import BaseModel, SecretStr, validator

from app import get_config


class UserModel(BaseModel):
    id: UUID = ...
    email: str = ...
    nickname: str = None
    password_hash = SecretStr
    photo: str = None
    is_admin: bool = False

    class Config:
        orm_mode = True

    @validator("photo", pre=True, always=True)
    def get_photo(cls, v, *, values, **kwargs):
        config = get_config()
        return f"{config.MEDIA_URL}/{v}"


class AuthModel(BaseModel):
    access_token: str
    refresh_token: str
    user: UserModel
