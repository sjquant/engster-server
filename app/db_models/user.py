from sqlalchemy.dialects.postgresql import UUID
from sanic.exceptions import ServerError

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hasher = PBKDF2PasswordHasher()

    def __repr__(self):
        return "<User {}>".format(self.email)

    def set_password(self, password: str):
        self.password_hash = self.hasher.create_password(password)

    def check_password(self, password: str) -> bool:
        """ check password """
        try:
            return self.hasher.verify_password(password, self.password_hash)
        except ValueError:
            raise ServerError("cannot interpret password.", status_code=422)
