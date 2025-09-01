from sqlmodel import SQLModel, Session, create_engine
import os

# Используем SQLite для тестирования (можно заменить на PostgreSQL)
db_url = 'sqlite:///./warriors.db'
engine = create_engine(db_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
