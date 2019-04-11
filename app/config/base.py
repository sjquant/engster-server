import os
import json
from dotenv import load_dotenv

# load env
ENVDIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ENVDIR, 'secrets/.env.base'))

ENV = os.getenv('ENV', 'local')

if ENV == 'local':
    load_dotenv(os.path.join(ENVDIR, 'secrets/.env.local'))
elif ENV == 'test':
    load_dotenv(os.path.join(ENVDIR, 'secrets/.env.test'))
elif ENV == 'production':
    load_dotenv(os.path.join(ENVDIR, 'secrets/.env.production'))

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

DB_PORT = '5432'
DB_DATABASE = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_URL = f'postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'

with open('app/config/settings.json') as f:
    SETTINGS = json.loads(f.read())
