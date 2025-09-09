from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from sqlalchemy import select
from app.schemas.finance import FinanceCreate, FinanceRead
from app.models.finance import Finance
from app.db.session import get_session
from app.api.v1.user import get_current_user_from_bearer

router = APIRouter()

@router.post("/", response_model=FinanceRead)
def create_finance(finance: FinanceCreate, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> FinanceRead:
    db_finance = Finance(**finance.dict(), user_id=current_user.id)
    db.add(db_finance)
    db.commit()
    db.refresh(db_finance)
    return FinanceRead.model_validate(db_finance, from_attributes=True)

@router.get("/", response_model=List[FinanceRead])
def read_finances(db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> List[FinanceRead]:
    finances = db.exec(select(Finance).where(Finance.user_id == current_user.id)).scalars().all()
    return [FinanceRead.model_validate(f, from_attributes=True) for f in finances]

@router.get("/{finance_id}", response_model=FinanceRead)
def read_finance(finance_id: int, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> FinanceRead:
    finance = db.get(Finance, finance_id)
    if not finance or finance.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Finance not found")
    return FinanceRead.model_validate(finance, from_attributes=True)

@router.delete("/{finance_id}")
def delete_finance(finance_id: int, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)):
    finance = db.get(Finance, finance_id)
    if not finance or finance.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Finance not found")
    db.delete(finance)
    db.commit()
    return {"ok": True} 