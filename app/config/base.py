import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PORT = "5432"
DB_DATABASE = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_URL = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
CSV_DOWNLOAD_PATH = os.getenv("CSV_DOWNLOAD_PATH", os.path.join(BASE_DIR, "data/csv"))
