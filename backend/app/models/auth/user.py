import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text

from app import db, bcrypt
from app.utils.basemodel import BaseModel


class User(BaseModel):
    """ User Model for storing user related details """
    __tablename__ = "user"

    id = db.Column(UUID, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    nickname = db.Column(db.String(10), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    photo = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<User {}>".format(self.email)

    async def create_user(self, email: str, nickname: str, password: str, is_admin: bool = False):
        self.id = uuid.uuid4()
        self.email = email
        self.username = nickname
        self.set_password(password)
        self.registered_on = datetime.datetime.now()
        self.is_admin = is_admin
        user = await self.create()
        return user

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """ check password """
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return super().to_dict(show=['id', 'email', 'nickname', 'photo'])
