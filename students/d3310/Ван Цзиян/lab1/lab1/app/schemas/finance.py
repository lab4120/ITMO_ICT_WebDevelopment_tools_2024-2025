from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class FinanceBase(BaseModel):
    amount: float
    type: str
    category_id: int
    description: Optional[str] = None

class FinanceCreate(FinanceBase):
    pass

class FinanceRead(FinanceBase):
    id: int
    user_id: int
    date: datetime

    class Config:
        from_attributes = True 