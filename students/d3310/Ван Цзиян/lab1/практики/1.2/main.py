from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from connection import engine, init_db, get_session
from models import Warrior, WarriorDefault, WarriorProfessions, Skill, Profession, ProfessionDefault, RaceType
from typing import TypedDict, List

app = FastAPI(title="Warriors API")

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Warriors API is running!"}

@app.get("/warriors/", response_model=List[Warrior])
def get_warriors(session: Session = Depends(get_session)):
    warriors = session.exec(select(Warrior)).all()
    return warriors

@app.get("/warriors_list")
def warriors_list(session: Session = Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()

@app.get("/warrior/{warrior_id}", response_model=WarriorProfessions)
def warriors_get(warrior_id: int, session: Session = Depends(get_session)) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    return warrior

@app.patch("/warrior/{warrior_id}")
def warrior_update(warrior_id: int, warrior: WarriorDefault, session: Session = Depends(get_session)) -> Warrior:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    
    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)
    
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

@app.post("/warrior")
def warriors_create(warrior: WarriorDefault, session: Session = Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior = Warrior.model_validate(warrior)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return {"status": 200, "data": warrior}

@app.get("/skills/", response_model=List[Skill])
def get_skills(session: Session = Depends(get_session)):
    skills = session.exec(select(Skill)).all()
    return skills

@app.post("/skills/", response_model=Skill)
def create_skill(skill: Skill, session: Session = Depends(get_session)):
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill

@app.get("/professions/", response_model=List[Profession])
def get_professions(session: Session = Depends(get_session)):
    professions = session.exec(select(Profession)).all()
    return professions

@app.get("/professions_list")
def professions_list(session: Session = Depends(get_session)) -> List[Profession]:
    return session.exec(select(Profession)).all()

@app.get("/profession/{profession_id}")
def profession_get(profession_id: int, session: Session = Depends(get_session)) -> Profession:
    return session.get(Profession, profession_id)

@app.post("/profession")
def profession_create(prof: ProfessionDefault, session: Session = Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Profession}):
    profession = Profession.model_validate(prof)
    session.add(profession)
    session.commit()
    session.refresh(profession)
    return {"status": 200, "data": profession}

@app.delete("/warrior/{warrior_id}")
def warrior_delete(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}

@app.delete("/profession/{profession_id}")
def profession_delete(profession_id: int, session: Session = Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    session.delete(profession)
    session.commit()
    return {"ok": True}

@app.delete("/skill/{skill_id}")
def skill_delete(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()
    return {"ok": True}
