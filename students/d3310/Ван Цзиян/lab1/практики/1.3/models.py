from typing import Optional
from sqlmodel import SQLModel, Field


class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class Warrior(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class SkillWarriorLink(SQLModel, table=True):
    skill_id: Optional[int] = Field(
        default=None, foreign_key="skill.id", primary_key=True
    )
    warrior_id: Optional[int] = Field(
        default=None, foreign_key="warrior.id", primary_key=True
    )
    level: int | None

