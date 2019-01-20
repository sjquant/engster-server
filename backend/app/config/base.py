import os
from dotenv import load_dotenv

# load env
ENVDIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ENVDIR, 'secrets/.env.base'))

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

DB_PORT = '5432'

BCRYPT_LOG_ROUNDS = 12
BCRYPT_HASH_PREFIX = '2b'
BCRYPT_HANDLE_LONG_PASSWORDS = False
