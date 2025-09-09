
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from app.api.v1 import user, finance, category, budget, goal, parser, async_parser
from app.db.init_db import init_db

app = FastAPI(
    title="Personal Finance Management Service",
    description="Сервис управления личными финансами с поддержкой JWT аутентификации",
    version="1.0.0",
    openapi_tags=[
        {"name": "users", "description": "Операции управления пользователями"},
        {"name": "finances", "description": "Операции управления финансами"},
        {"name": "categories", "description": "Операции управления категориями"},
        {"name": "budgets", "description": "Операции управления бюджетами"},
        {"name": "goals", "description": "Операции управления целями"},
        {"name": "parser", "description": "Вызов сервиса парсера"},
        {"name": "async-parser", "description": "Асинхронный вызов сервиса парсера через Celery"},
    ]
)

templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
async def startup_event():
    """Инициализация базы данных при запуске приложения"""
    init_db()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
app.include_router(finance.router, prefix="/api/v1/finances", tags=["finances"])
app.include_router(category.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(budget.router, prefix="/api/v1/budgets", tags=["budgets"])
app.include_router(goal.router, prefix="/api/v1/goals", tags=["goals"])
app.include_router(parser.router, prefix="/api/v1/parser", tags=["parser"])
app.include_router(async_parser.router, prefix="/api/v1/async-parser", tags=["async-parser"]) 