from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


# Race enumeration
class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


# Skill model
class Skill(BaseModel):
    id: int
    name: str
    description: str


# Profession model
class Profession(BaseModel):
    id: int
    title: str
    description: str


# Warrior model and race enumeration
class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession: Profession
    skills: Optional[List[Skill]] = []


