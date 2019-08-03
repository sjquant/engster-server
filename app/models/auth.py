from uuid import UUID
from pydantic import BaseModel, SecretStr


class UserModel(BaseModel):
    id: UUID = ...
    email: str = ...
    nickname: str = None
    password_hash = SecretStr
    photo: str = None
    is_admin: bool = False

    class Config:
        orm_mode = True


class AuthModel(BaseModel):
    access_token: str
    refresh_token: str
    user: UserModel
