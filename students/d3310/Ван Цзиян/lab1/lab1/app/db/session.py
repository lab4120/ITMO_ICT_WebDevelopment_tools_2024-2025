from sqlmodel import Session, create_engine
from sqlalchemy.engine import Engine
from app.core.config import settings

# Create engine with minimal configuration
engine: Engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session 