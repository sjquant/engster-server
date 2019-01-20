import jwt
import datetime
from app import db, bcrypt


class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False, **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.is_admin = admin

    def __repr__(self):
        return "User <{}>".format(self.email)

    def check_password(self, password: str) -> bool:
        """ check password """
        return bcrypt.check_password(self.password_hash, password)
