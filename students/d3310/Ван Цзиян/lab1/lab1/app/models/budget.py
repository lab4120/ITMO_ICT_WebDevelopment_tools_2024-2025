from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    period: str  # 如 'monthly', 'yearly'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

    user: "User" = Relationship(back_populates="budgets")
    category: "Category" = Relationship(back_populates="budgets") 