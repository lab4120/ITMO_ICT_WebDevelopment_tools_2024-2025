from app.models import user, category, budget, finance, goal, association
from sqlmodel import SQLModel

# Import all models to ensure they are registered with SQLModel
# This is required for Alembic to detect all models 