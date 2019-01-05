from .base import *

# load env
load_dotenv(os.path.join(ENVDIR, 'secrets/.env.production'))

ENV = 'production'
DEBUG = False
