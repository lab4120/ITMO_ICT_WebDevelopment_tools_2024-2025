from fastapi import FastAPI
from models import Warrior, RaceType, Profession, Skill

app = FastAPI()

# Virtual database for testing API interaction (expanded with skills)
temp_bd = [{
    "id": 1,
    "race": "director",
    "name": "Мартынов Дмитрий",
    "level": 12,
    "profession": {
        "id": 1,
        "title": "Влиятельный человек",
        "description": "Эксперт по всем вопросам"
    },
    "skills": [
        {
            "id": 1,
            "name": "Купле-продажа компрессоров",
            "description": ""
        },
        {
            "id": 2,
            "name": "Оценка имущества",
            "description": ""
        }
    ]
},
{
    "id": 2,
    "race": "worker",
    "name": "Андрей Косякин",
    "level": 12,
    "profession": {
        "id": 1,
        "title": "Дельфист-гребец",
        "description": "Уважаемый сотрудник"
    },
    "skills": []
},
]


@app.get("/")
def hello() -> str:
    return "Hello, [username]!"


# CRUD API Endpoints

@app.get("/warriors_list")
def warriors_list():
    return temp_bd


@app.get("/warrior/{warrior_id}")
def get_warrior_by_id(warrior_id: int):
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]


@app.post("/warrior")
def create_warrior(warrior: Warrior):
    temp_bd.append(warrior.dict())
    return {"status": 200, "data": warrior}


@app.delete("/warrior/delete/{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/warrior/{warrior_id}")
def warrior_update(warrior_id: int, warrior: Warrior):
    for i, war in enumerate(temp_bd):
        if war.get("id") == warrior_id:
            temp_bd[i] = warrior.dict()
    return temp_bd
