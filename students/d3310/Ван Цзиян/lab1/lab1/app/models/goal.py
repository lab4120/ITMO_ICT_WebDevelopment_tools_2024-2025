from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    target_amount: float
    current_amount: float = 0
    deadline: Optional[datetime] = None
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="goals") 