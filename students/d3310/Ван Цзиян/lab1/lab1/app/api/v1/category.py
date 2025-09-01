from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlalchemy import select
from typing import List
from app.schemas.category import CategoryCreate, CategoryRead
from app.models.category import Category
from app.db.session import get_session
from app.api.v1.user import get_current_user_from_bearer

router = APIRouter()

@router.post("/", response_model=CategoryRead)
def create_category(category: CategoryCreate, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> CategoryRead:
    db_category = Category(**category.model_dump(), user_id=current_user.id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return CategoryRead.model_validate(db_category, from_attributes=True)

@router.get("/", response_model=List[CategoryRead])
def read_categories(db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> List[CategoryRead]:
    categories = db.exec(select(Category).where(Category.user_id == current_user.id)).scalars().all()
    return [CategoryRead.model_validate(cat, from_attributes=True) for cat in categories]

@router.get("/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> CategoryRead:
    category = db.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryRead.model_validate(category, from_attributes=True)

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)):
    category = db.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"ok": True} 