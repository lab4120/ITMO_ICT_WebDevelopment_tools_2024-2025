from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from sqlalchemy import select
from app.schemas.goal import GoalCreate, GoalRead
from app.models.goal import Goal
from app.db.session import get_session
from app.api.v1.user import get_current_user_from_bearer

router = APIRouter()

@router.post("/", response_model=GoalRead)
def create_goal(goal: GoalCreate, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> GoalRead:
    db_goal = Goal(**goal.dict(), user_id=current_user.id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return GoalRead.model_validate(db_goal, from_attributes=True)

@router.get("/", response_model=List[GoalRead])
def read_goals(db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> List[GoalRead]:
    goals = db.exec(select(Goal).where(Goal.user_id == current_user.id)).scalars().all()
    return [GoalRead.model_validate(g, from_attributes=True) for g in goals]

@router.get("/{goal_id}", response_model=GoalRead)
def read_goal(goal_id: int, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)) -> GoalRead:
    goal = db.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
    return GoalRead.model_validate(goal, from_attributes=True)

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_session), current_user=Depends(get_current_user_from_bearer)):
    goal = db.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return {"ok": True} 