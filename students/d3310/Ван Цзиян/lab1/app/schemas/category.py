from typing import Optional
from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True