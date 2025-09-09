from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Finance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    type: str  # 'income' или 'expense'
    date: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

    user: "User" = Relationship(back_populates="finances")
    category: "Category" = Relationship(back_populates="finances") 