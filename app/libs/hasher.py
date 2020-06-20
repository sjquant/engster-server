"""
I referenced django's utils/crypto.py, and contrib/hashers.py
"""

import hashlib
import hmac
import secrets
import base64

# This will never be a valid encoded hash
UNUSABLE_PASSWORD_PREFIX = "!"
# number of random chars to add after UNUSABLE_PASSWORD_PREFIX
UNUSABLE_PASSWORD_SUFFIX_LENGTH = 40


def force_bytes(s, encoding="utf-8"):
    if isinstance(s, bytes):
        return s
    else:
        return str(s).encode(encoding)


def get_random_string(
    length=12,
    allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
):

    return "".join(secrets.choice(allowed_chars) for i in range(length))


def constant_time_compare(val1, val2):
    """Return True if the two strings are equal, False otherwise."""
    return hmac.compare_digest(force_bytes(val1), force_bytes(val2))


def pbkdf2(password, salt, iterations, dklen=0, digest=None):
    """Return the hash of password using pbkdf2."""
    if digest is None:
        digest = hashlib.sha256
    dklen = dklen or None
    password = force_bytes(password)
    salt = force_bytes(salt)
    return hashlib.pbkdf2_hmac(digest().name, password, salt, iterations, dklen)


class PBKDF2PasswordHasher:
    """
    Secure password hashing using the PBKDF2 algorithm (recommended)
    Configured to use PBKDF2 + HMAC + SHA256.
    The result is a 64 byte binary string.  Iterations may be changed
    safely but you must rename the algorithm if you change SHA256.
    """

    algorithm = "pbkdf2_sha256"
    iterations = 180000
    digest = hashlib.sha256

    @property
    def salt(self):
        return get_random_string()

    def encode(self, password, salt, iterations=None):
        assert password is not None

        iterations = iterations or self.iterations
        hash = pbkdf2(password, salt, iterations, digest=self.digest)
        hash = base64.b64encode(hash).decode("ascii").strip()
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, hash)

    def verify_password(self, password, encoded):
        algorithm, iterations, salt, hash = encoded.split("$", 3)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt, int(iterations))
        return constant_time_compare(encoded, encoded_2)

    def create_password(self, password):
        if password is None:
            return UNUSABLE_PASSWORD_PREFIX + get_random_string(
                UNUSABLE_PASSWORD_SUFFIX_LENGTH
            )
        return self.encode(password, self.salt)
