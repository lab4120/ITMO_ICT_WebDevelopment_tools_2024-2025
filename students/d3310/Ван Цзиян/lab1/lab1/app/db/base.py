from app.models import user, category, budget, finance, goal, association
from sqlmodel import SQLModel

# 只需导入所有模型，供 Alembic 使用 