from .base import *

# load env
load_dotenv(os.path.join(ENVDIR, 'secrets/.env.local'))

ENV = 'development'
DEBUG = True

DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
