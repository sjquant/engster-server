import os
from dotenv import load_dotenv

# load env
ENVDIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ENVDIR, 'secrets/.env.base'))
