from base64 import b64decode, b64encode
from typing import Union

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class PasswordHasher(object):

    def __init__(self, app=None):
        self._app = app
        self._salt = None

    def init_app(self, app):
        self._app = app

    @property
    def kdf(self):
        return PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=self._app.config.get('PWIterations', 120000),
            backend=default_backend()
        )

    @property
    def salt(self) -> bytes:
        if self._salt is None:
            self._salt = self._app.config.get(
                'SECRET_KEY', None).encode()
        return self._salt

    def generate_password_hash(self, password: Union[str, bytes]) -> str:
        """ generate hashed password using PBKDF2HMAC """

        if not isinstance(password, bytes):
            password = str.encode(password)
        password_hash = b64encode(self.kdf.derive(password)).decode()
        return password_hash

    def check_password(self, password_hash: str, password: str) -> bool:
        """ check password """

        if not isinstance(password, bytes):
            password = str.encode(password)
        password_hash = b64decode(password_hash.encode())
        try:
            self.kdf.verify(password, password_hash)
            verified = True
        except:
            verified = False
        return verified
