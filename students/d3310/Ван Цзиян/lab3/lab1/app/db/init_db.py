from sqlmodel import SQLModel
from app.db.session import engine
import app.db.base

def init_db():
    """Инициализация базы данных"""
    SQLModel.metadata.create_all(engine)
    print("✅ Таблицы базы данных созданы")

if __name__ == "__main__":
    init_db()