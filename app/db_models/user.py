from typing import Optional
import uuid
import secrets
import random

from sqlalchemy.dialects.postgresql import UUID

from app import db
from app.libs.hasher import PBKDF2PasswordHasher
from .base_models import TimeStampedModel


class User(TimeStampedModel):
    """ User Model for storing user related details """

    __tablename__ = "user"

    id = db.Column(UUID, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    nickname = db.Column(db.String(10), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self):
        super().__init__()
        self.hasher = PBKDF2PasswordHasher()

    def __repr__(self):
        return "<User {}>".format(self.email)

    def generate_random_nickname(self):
        """ generate random nickname when user didn't enter nickname """
        allowed_prefix_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        allowed_suffix_chars = "abcdefghizklmnopqrstuvwxyz0123456789!@#$%^&*="

        prefix = "".join(secrets.choice(allowed_prefix_chars) for i in range(4))
        suffix = "".join(
            secrets.choice(allowed_suffix_chars) for i in range(random.randint(1, 6))
        )
        return prefix + suffix

    async def create_user(
        self,
        email: str,
        password: str,
        nickname: Optional[str] = None,
        is_admin: bool = False,
    ):
        self.id = uuid.uuid4()
        self.email = email
        self.nickname = nickname or self.generate_random_nickname()
        self.set_password(password)
        self.is_admin = is_admin
        user = await self.create()
        return user

    def set_password(self, password: str):
        self.password_hash = self.hasher.create_password(password)

    def check_password(self, password: str) -> bool:
        """ check password """
        return self.hasher.verify_password(password, self.password_hash)
