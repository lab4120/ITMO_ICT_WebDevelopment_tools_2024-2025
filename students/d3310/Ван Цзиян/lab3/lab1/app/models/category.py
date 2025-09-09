from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="categories")
    budgets: List["Budget"] = Relationship(back_populates="category")
    finances: List["Finance"] = Relationship(back_populates="category") 