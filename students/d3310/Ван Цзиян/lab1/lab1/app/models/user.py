from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    categories: List["Category"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    finances: List["Finance"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user") 