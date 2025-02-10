import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_default_secret")
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", "your_default_refresh_secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

settings = Settings()