from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from sqlalchemy import select
from app.schemas.budget import BudgetCreate, BudgetRead
from app.models.budget import Budget
from app.db.session import get_session
from app.api.v1.user import get_current_user_from_bearer

router = APIRouter()

@router.post("/", response_model=BudgetRead)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> BudgetRead:
    db_budget = Budget(**budget.dict(), user_id=current_user.id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.get("/", response_model=List[BudgetRead])
def read_budgets(db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> List[BudgetRead]:
    budgets = db.exec(select(Budget).where(Budget.user_id == current_user.id)).scalars().all()
    return [BudgetRead.model_validate(b) for b in budgets]

@router.get("/{budget_id}", response_model=BudgetRead)
def read_budget(budget_id: int, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> BudgetRead:
    budget = db.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")
    return BudgetRead.model_validate(budget)

@router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)):
    budget = db.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()
    return {"ok": True} 