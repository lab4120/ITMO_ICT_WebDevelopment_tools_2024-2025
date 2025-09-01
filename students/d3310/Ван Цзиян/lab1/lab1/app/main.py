from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from app.api.v1 import user, finance, category, budget, goal

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
    ]
)

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
app.include_router(finance.router, prefix="/api/v1/finances", tags=["finances"])
app.include_router(category.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(budget.router, prefix="/api/v1/budgets", tags=["budgets"])
app.include_router(goal.router, prefix="/api/v1/goals", tags=["goals"]) 