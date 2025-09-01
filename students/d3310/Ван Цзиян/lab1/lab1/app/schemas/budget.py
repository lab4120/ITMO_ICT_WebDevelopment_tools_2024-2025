from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class BudgetBase(BaseModel):
    amount: float
    period: str
    category_id: int

class BudgetCreate(BudgetBase):
    pass

class BudgetRead(BudgetBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True 