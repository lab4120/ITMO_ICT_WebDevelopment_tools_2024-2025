# Личный Финансовый Менеджер - Отчет о лабораторной работе

## Обзор проекта

Данный проект представляет собой сервис управления личными финансами на базе FastAPI, реализующий полную систему аутентификации пользователей, управления финансами, бюджетами и целями.

## Техническая архитектура

- **Backend Framework**: FastAPI
- **Database ORM**: SQLModel (на основе SQLAlchemy)
- **Database**: SQLite
- **Authentication**: JWT (JSON Web Tokens)
- **Password Encryption**: bcrypt
- **Frontend Templates**: Jinja2Templates
- **API Documentation**: Swagger UI

## Структура проекта

```
lab1/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── user.py          # API управления пользователями
│   │   │   ├── finance.py       # API управления финансами
│   │   │   ├── category.py      # API управления категориями
│   │   │   ├── budget.py        # API управления бюджетами
│   │   │   └── goal.py          # API управления целями
│   │   └── deps.py              # Dependency Injection
│   ├── core/
│   │   ├── config.py            # Управление конфигурацией
│   │   └── security.py          # Функции безопасности
│   ├── crud/
│   │   └── user.py              # CRUD операции для пользователей
│   ├── db/
│   │   ├── base.py              # Базовая конфигурация БД
│   │   ├── init_db.py           # Инициализация БД
│   │   └── session.py           # Управление сессиями БД
│   ├── models/
│   │   ├── user.py              # Модель пользователя
│   │   ├── finance.py           # Модель финансов
│   │   ├── category.py          # Модель категории
│   │   ├── budget.py            # Модель бюджета
│   │   ├── goal.py              # Модель цели
│   │   └── association.py       # Модель ассоциации
│   ├── schemas/
│   │   ├── user.py              # Схема данных пользователя
│   │   ├── finance.py           # Схема данных финансов
│   │   ├── category.py          # Схема данных категории
│   │   ├── budget.py            # Схема данных бюджета
│   │   ├── goal.py              # Схема данных цели
│   │   └── association.py        # Схема данных ассоциации
│   ├── templates/
│   │   └── index.html           # Шаблон главной страницы
│   └── main.py                  # Точка входа приложения
├── docs/
│   └── index.md                 # Данный документ
├── requirements.txt             # Список зависимостей
└── README.md                    # Описание проекта
```

## Функции управления пользователями

### Модель пользователя (app/models/user.py)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### API эндпоинты пользователей (app/api/v1/user.py)

#### 1. Регистрация пользователя
- **Эндпоинт**: `POST /api/v1/users/register`
- **Функция**: Создание нового пользовательского аккаунта
- **Тело запроса**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```

#### 2. Вход пользователя
- **Эндпоинт**: `POST /api/v1/users/login`
- **Функция**: Вход пользователя и получение JWT токена
- **Тело запроса**: `application/x-www-form-urlencoded`
  ```
  username=string&password=string
  ```
- **Ответ**:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```

#### 3. Получение информации о текущем пользователе
- **Эндпоинт**: `GET /api/v1/users/me`
- **Функция**: Получение информации о текущем авторизованном пользователе
- **Аутентификация**: Bearer Token обязателен

#### 4. Получение всех пользователей
- **Эндпоинт**: `GET /api/v1/users/`
- **Функция**: Получение списка всех пользователей
- **Аутентификация**: Bearer Token обязателен

#### 5. Изменение пароля
- **Эндпоинт**: `POST /api/v1/users/change-password`
- **Функция**: Изменение пароля пользователя
- **Аутентификация**: Bearer Token обязателен
- **Тело запроса**:
  ```json
  {
    "old_password": "string",
    "new_password": "string"
  }
  ```

## Функции управления финансами

### Модель финансов (app/models/finance.py)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Finance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    type: str  # "income" or "expense"
    category_id: int = Field(foreign_key="category.id")
    description: str
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### API эндпоинты финансов (app/api/v1/finance.py)

#### 1. Создание финансовой записи
- **Эндпоинт**: `POST /api/v1/finances/`
- **Функция**: Создание новой финансовой записи
- **Аутентификация**: Bearer Token обязателен
- **Тело запроса**:
  ```json
  {
    "amount": 0.0,
    "type": "string",
    "category_id": 0,
    "description": "string"
  }
  ```

#### 2. Получение списка финансовых записей
- **Эндпоинт**: `GET /api/v1/finances/`
- **Функция**: Получение всех финансовых записей текущего пользователя
- **Аутентификация**: Bearer Token обязателен

#### 3. Получение отдельной финансовой записи
- **Эндпоинт**: `GET /api/v1/finances/{finance_id}`
- **Функция**: Получение указанной финансовой записи
- **Аутентификация**: Bearer Token обязателен

#### 4. Обновление финансовой записи
- **Эндпоинт**: `PUT /api/v1/finances/{finance_id}`
- **Функция**: Обновление указанной финансовой записи
- **Аутентификация**: Bearer Token обязателен

#### 5. Удаление финансовой записи
- **Эндпоинт**: `DELETE /api/v1/finances/{finance_id}`
- **Функция**: Удаление указанной финансовой записи
- **Аутентификация**: Bearer Token обязателен

## Функции управления категориями

### Модель категории (app/models/category.py)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### API эндпоинты категорий (app/api/v1/category.py)

#### 1. Создание категории
- **Эндпоинт**: `POST /api/v1/categories/`
- **Функция**: Создание новой финансовой категории
- **Аутентификация**: Bearer Token обязателен

#### 2. Получение списка категорий
- **Эндпоинт**: `GET /api/v1/categories/`
- **Функция**: Получение всех категорий текущего пользователя
- **Аутентификация**: Bearer Token обязателен

#### 3. Получение отдельной категории
- **Эндпоинт**: `GET /api/v1/categories/{category_id}`
- **Функция**: Получение указанной категории
- **Аутентификация**: Bearer Token обязателен

#### 4. Обновление категории
- **Эндпоинт**: `PUT /api/v1/categories/{category_id}`
- **Функция**: Обновление указанной категории
- **Аутентификация**: Bearer Token обязателен

#### 5. Удаление категории
- **Эндпоинт**: `DELETE /api/v1/categories/{category_id}`
- **Функция**: Удаление указанной категории
- **Аутентификация**: Bearer Token обязателен

## Функции управления бюджетами

### Модель бюджета (app/models/budget.py)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    period: str  # "daily", "weekly", "monthly", "yearly"
    category_id: int = Field(foreign_key="category.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### API эндпоинты бюджетов (app/api/v1/budget.py)

#### 1. Создание бюджета
- **Эндпоинт**: `POST /api/v1/budgets/`
- **Функция**: Создание нового бюджета
- **Аутентификация**: Bearer Token обязателен
- **Тело запроса**:
  ```json
  {
    "amount": 0.0,
    "period": "string",
    "category_id": 0
  }
  ```

#### 2. Получение списка бюджетов
- **Эндпоинт**: `GET /api/v1/budgets/`
- **Функция**: Получение всех бюджетов текущего пользователя
- **Аутентификация**: Bearer Token обязателен

#### 3. Получение отдельного бюджета
- **Эндпоинт**: `GET /api/v1/budgets/{budget_id}`
- **Функция**: Получение указанного бюджета
- **Аутентификация**: Bearer Token обязателен

#### 4. Обновление бюджета
- **Эндпоинт**: `PUT /api/v1/budgets/{budget_id}`
- **Функция**: Обновление указанного бюджета
- **Аутентификация**: Bearer Token обязателен

#### 5. Удаление бюджета
- **Эндпоинт**: `DELETE /api/v1/budgets/{budget_id}`
- **Функция**: Удаление указанного бюджета
- **Аутентификация**: Bearer Token обязателен

## Функции управления целями

### Модель цели (app/models/goal.py)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    target_amount: float
    current_amount: float = Field(default=0.0)
    deadline: datetime
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### API эндпоинты целей (app/api/v1/goal.py)

#### 1. Создание цели
- **Эндпоинт**: `POST /api/v1/goals/`
- **Функция**: Создание новой финансовой цели
- **Аутентификация**: Bearer Token обязателен
- **Тело запроса**:
  ```json
  {
    "name": "string",
    "target_amount": 0.0,
    "current_amount": 0.0,
    "deadline": "2023-12-31T23:59:59"
  }
  ```

#### 2. Получение списка целей
- **Эндпоинт**: `GET /api/v1/goals/`
- **Функция**: Получение всех целей текущего пользователя
- **Аутентификация**: Bearer Token обязателен

#### 3. Получение отдельной цели
- **Эндпоинт**: `GET /api/v1/goals/{goal_id}`
- **Функция**: Получение указанной цели
- **Аутентификация**: Bearer Token обязателен

#### 4. Обновление цели
- **Эндпоинт**: `PUT /api/v1/goals/{goal_id}`
- **Функция**: Обновление указанной цели
- **Аутентификация**: Bearer Token обязателен

#### 5. Удаление цели
- **Эндпоинт**: `DELETE /api/v1/goals/{goal_id}`
- **Функция**: Удаление указанной цели
- **Аутентификация**: Bearer Token обязателен

## Подключение к базе данных

### Управление сессиями базы данных (app/db/session.py)

```python
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

engine = create_engine(settings.database_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
```

### Инициализация базы данных (app/db/init_db.py)

```python
from sqlmodel import SQLModel
from app.db.session import engine
import app.db.base
from sqlmodel import Session, select
from app.models.category import Category
from app.models.user import User

def init_db():
    """Инициализация базы данных"""
    SQLModel.metadata.create_all(engine)

    # Создание категорий по умолчанию
    with Session(engine) as session:
        existing_categories = session.exec(select(Category)).all()

        if not existing_categories:
            income_category = Category(name="Income", user_id=1)
            expense_category = Category(name="Expenses", user_id=1)

            session.add(income_category)
            session.add(expense_category)
            session.commit()
            print("Категории по умолчанию созданы:")
            print("   - category_id=1: Income (доходы)")
            print("   - category_id=2: Expenses (расходы)")
        else:
            print("Категории уже существуют, пропускаем создание")

if __name__ == "__main__":
    init_db()
```

## Конфигурация безопасности

### JWT конфигурация (app/core/security.py)

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
```

## Фронтенд интерфейс

### Главная страница (app/templates/index.html)

Главная страница предоставляет современный интерфейс дашборда, включающий:

- **Форма входа пользователя**: Поддержка входа по имени пользователя и паролю
- **Финансовый обзор**: Отображение общего дохода, общих расходов, общего бюджета и общих целей
- **Умные напоминания о бюджете**: Автоматическое отображение предупреждений или подтверждений на основе доходов, расходов и бюджета
- **Адаптивный дизайн**: Адаптация к различным размерам экранов

### Основные функциональные возможности

1. **JWT аутентификация**: Полная система аутентификации пользователей
2. **Шифрование паролей**: Использование bcrypt для хеширования паролей
3. **Управление бюджетом**: Поддержка отображения положительных и отрицательных бюджетов с напоминаниями
4. **Данные в реальном времени**: Динамическая загрузка и отображение финансовых данных
5. **Пользовательский интерфейс**: Интуитивный интерфейс и сообщения об ошибках

## Инструкции по запуску

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Инициализация базы данных
```bash
python -m app.db.init_db
```

### 3. Запуск сервера
```bash
uvicorn app.main:app --reload
```

### 4. Доступ к приложению
- Главная страница: http://127.0.0.1:8000/
- Документация API: http://127.0.0.1:8000/docs

## Сводка API эндпоинтов

| Метод | Эндпоинт | Функция | Аутентификация |
|-------|----------|---------|----------------|
| POST | `/api/v1/users/register` | Регистрация пользователя | Нет |
| POST | `/api/v1/users/login` | Вход пользователя | Нет |
| GET | `/api/v1/users/me` | Получение текущего пользователя | Да |
| GET | `/api/v1/users/` | Получение всех пользователей | Да |
| POST | `/api/v1/users/change-password` | Изменение пароля | Да |
| POST | `/api/v1/finances/` | Создание финансовой записи | Да |
| GET | `/api/v1/finances/` | Получение финансовых записей | Да |
| GET | `/api/v1/finances/{id}` | Получение отдельной финансовой записи | Да |
| PUT | `/api/v1/finances/{id}` | Обновление финансовой записи | Да |
| DELETE | `/api/v1/finances/{id}` | Удаление финансовой записи | Да |
| POST | `/api/v1/categories/` | Создание категории | Да |
| GET | `/api/v1/categories/` | Получение списка категорий | Да |
| GET | `/api/v1/categories/{id}` | Получение отдельной категории | Да |
| PUT | `/api/v1/categories/{id}` | Обновление категории | Да |
| DELETE | `/api/v1/categories/{id}` | Удаление категории | Да |
| POST | `/api/v1/budgets/` | Создание бюджета | Да |
| GET | `/api/v1/budgets/` | Получение списка бюджетов | Да |
| GET | `/api/v1/budgets/{id}` | Получение отдельного бюджета | Да |
| PUT | `/api/v1/budgets/{id}` | Обновление бюджета | Да |
| DELETE | `/api/v1/budgets/{id}` | Удаление бюджета | Да |
| POST | `/api/v1/goals/` | Создание цели | Да |
| GET | `/api/v1/goals/` | Получение списка целей | Да |
| GET | `/api/v1/goals/{id}` | Получение отдельной цели | Да |
| PUT | `/api/v1/goals/{id}` | Обновление цели | Да |
| DELETE | `/api/v1/goals/{id}` | Удаление цели | Да |

## GitHub ссылки

**Репозиторий проекта**: [Личный Финансовый Менеджер](https://github.com/lab4120/ITMO_ICT_WebDevelopment_tools_2024-2025/tree/main/students/d3310/Ван%20Цзиянь/lab1/lab1)

**Основная ветка**: `main`

**Ключевые коммиты**:
- Начальная настройка проекта
- Реализация системы аутентификации пользователей
- Завершение функций управления финансами
- Реализация функций управления бюджетом
- Оптимизация фронтенд интерфейса
- Выпуск финальной версии

---

*Данный отчет содержит полное содержание лабораторной работы, включая все реализованные эндпоинты, модели и код подключения к базе данных. Проект использует фреймворк FastAPI и реализует полную функциональность управления личными финансами с поддержкой аутентификации пользователей, управления финансами, бюджетами и целями.* 