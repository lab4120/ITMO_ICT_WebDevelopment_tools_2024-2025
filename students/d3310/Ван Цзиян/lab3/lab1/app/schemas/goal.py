from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class GoalBase(BaseModel):
    name: str
    target_amount: float
    deadline: Optional[datetime] = None

class GoalCreate(GoalBase):
    pass

class GoalRead(GoalBase):
    id: int
    user_id: int
    current_amount: float

    class Config:
        from_attributes = True