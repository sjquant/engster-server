import os
import datetime
import json

ENV = os.getenv("ENV")
DEBUG = False if ENV == "production" else True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_URL = os.getenv("MEDIA_URL")

# Cors
CORS_ORIGINS = os.getenv("CORS", "*").split(",")

# DB
DB_PORT = "5432"
DB_DATABASE = os.getenv("DB_NAME", "engster")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_URL = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

# JWT
JWT = {
    "secret_key": os.getenv("JWT_SECRET_KEY", "secret_key"),
    "access_expires": datetime.timedelta(os.getenv("JWT_ACCESS_EXPIRES", 10080))
}

# Social Auth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FB_CLIENT_ID = os.getenv("FB_CLIENT_ID")
FB_CLIENT_SECRET = os.getenv("FB_CLIENT_SECRET")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

CSV_DOWNLOAD_PATH = os.getenv("CSV_DOWNLOAD_PATH", os.path.join(BASE_DIR, "data/csv"))