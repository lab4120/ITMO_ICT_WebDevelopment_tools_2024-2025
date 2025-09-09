import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

class Settings:
    """Класс настроек приложения"""
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    PARSER_URL: str = os.getenv("PARSER_URL", "http://parser:8001")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Глобальный экземпляр настроек
settings = Settings() 