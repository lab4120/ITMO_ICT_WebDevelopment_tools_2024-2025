from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum
import sqlalchemy as sa

class RaceType(str, Enum):
    director = "director"
    worker = "worker"
    junior = "junior"

class SkillWarriorLink(SQLModel, table=True):
    skill_id: Optional[int] = Field(default=None, foreign_key="skill.id", primary_key=True)
    warrior_id: Optional[int] = Field(default=None, foreign_key="warrior.id", primary_key=True)

class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    warriors: Optional[List["Warrior"]] = Relationship(
        back_populates="skills", link_model=SkillWarriorLink
    )

class Profession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    warriors_prof: List["Warrior"] = Relationship(
        back_populates="profession",
        sa_relationship_kwargs={
            "cascade": "all, delete",
        },
    )

# Входная модель для создания воина (без id и связей)
class WarriorDefault(SQLModel):
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")

# Модель-наследник для отображения связей с профессией
class WarriorProfessions(WarriorDefault):
    profession: Optional[Profession] = None

# Полная модель воина с таблицей и связями
class Warrior(WarriorDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profession: Optional[Profession] = Relationship(
        back_populates="warriors_prof",
        sa_relationship_kwargs={
            "cascade": "all, delete",
        },
    )
    skills: Optional[List[Skill]] = Relationship(
        back_populates="warriors", link_model=SkillWarriorLink
    )

# Входная модель для создания профессии
class ProfessionDefault(SQLModel):
    title: str
    description: str
