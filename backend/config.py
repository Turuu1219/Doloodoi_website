"""
backend/config.py
All app configuration loaded from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY         = os.getenv("SECRET_KEY", "change-me-minimum-32-chars-long!")
    DEBUG              = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Database
    DB_HOST            = os.getenv("DB_HOST", "localhost")
    DB_PORT            = int(os.getenv("DB_PORT", 3306))
    DB_USER            = os.getenv("DB_USER", "school_user")
    DB_PASSWORD        = os.getenv("DB_PASSWORD", "school_pass")
    DB_NAME            = os.getenv("DB_NAME", "doloodoi_db")

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{os.getenv('DB_USER','school_user')}"
        f":{os.getenv('DB_PASSWORD','school_pass')}"
        f"@{os.getenv('DB_HOST','localhost')}"
        f":{os.getenv('DB_PORT',3306)}"
        f"/{os.getenv('DB_NAME','doloodoi_db')}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle":  300,
    }

    # Uploads
    UPLOAD_FOLDER      = os.getenv("UPLOAD_FOLDER", os.path.join("frontend", "static", "uploads"))
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024   # 10 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # Session
    SESSION_HOURS      = int(os.getenv("SESSION_HOURS", 8))

    # CORS
    CORS_ORIGINS       = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5000,http://127.0.0.1:5000"
    ).split(",")

    # Rate limits
    RATELIMIT_DEFAULT        = os.getenv("RATELIMIT_DEFAULT",  "200 per minute")
    RATELIMIT_LOGIN          = os.getenv("RATELIMIT_LOGIN",    "10 per minute")
    RATELIMIT_SUBMIT         = os.getenv("RATELIMIT_SUBMIT",   "5 per minute")
    RATELIMIT_STORAGE_URL    = "memory://"
