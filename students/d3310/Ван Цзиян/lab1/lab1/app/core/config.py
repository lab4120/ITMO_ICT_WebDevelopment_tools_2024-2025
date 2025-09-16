import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Use hardcoded connection string to avoid encoding issues
    DATABASE_URL: str = "postgresql://postgres:221bbs@localhost:5432/finance_db"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings() 