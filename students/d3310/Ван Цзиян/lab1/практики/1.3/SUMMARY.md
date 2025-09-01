# Практика 1.3. Миграции, ENV, GitIgnore и структура проекта

## Обзор
В данной практике мы настроили систему миграций базы данных с использованием Alembic, конфигурацию переменных окружения и файл .gitignore для Python проекта с FastAPI и SQLModel.

## Выполненные задачи

### 1. Настройка Alembic для миграций

#### Установка и инициализация
```bash
pip install alembic
alembic init migrations
```

#### Структура проекта после инициализации
```
migrations/
├── versions/          # Папка для файлов миграций
├── env.py            # Конфигурация окружения
├── README            # Документация
└── script.py.mako    # Шаблон для миграций
alembic.ini           # Основной конфигурационный файл
```

#### Конфигурация env.py
```python
from models import *  # Импорт всех моделей
target_metadata = SQLModel.metadata  # Метаданные для автогенерации
```

#### Конфигурация script.py.mako
```python
import sqlmodel  # Добавлен импорт sqlmodel
```

#### Конфигурация alembic.ini
```ini
sqlalchemy.url = sqlite:///./test.db
```

### 2. Создание моделей SQLModel

#### models.py
```python
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
    level: int | None  # Добавленное поле level
```

### 3. Создание и применение миграций

#### Генерация миграции
```bash
alembic revision --autogenerate -m "skill added"
```

#### Применение миграции
```bash
alembic upgrade head
```

### 4. Настройка переменных окружения

#### Установка python-dotenv
```bash
pip install python-dotenv
```

#### Создание .env файла
```
DB_ADMIN=postgresql://postgres:123@localhost/warriors_db
```

#### Пример использования в Python
```python
import os
from dotenv import load_dotenv

load_dotenv('.env')
db_url = os.getenv('DB_ADMIN')
```

### 5. Настройка .gitignore

#### Основные исключения
- **IDE**: `.idea`, `.vscode`
- **Python**: `__pycache__`, `*.pyc`, `venv`, `env`
- **База данных**: `test.db`, `*.db`
- **Переменные окружения**: `*.env`, `.env`
- **Логи**: `log.txt`, `*.log`
- **Кэш**: `.cache`, `.mypy_cache`, `.pytest_cache`
- **Архивы**: `docs.zip`, `archive.zip`
- **Системные файлы**: `.DS_Store` (macOS)

## Итоговая структура проекта

```
1.3/
├── .env                 # Переменные окружения (исключен из Git)
├── .gitignore          # Конфигурация исключений Git
├── alembic.ini         # Конфигурация Alembic
├── models.py           # Модели SQLModel
├── config_example.py   # Пример использования переменных окружения
├── test.db             # База данных SQLite (исключена из Git)
└── migrations/         # Директория миграций
    ├── env.py          # Конфигурация окружения миграций
    ├── script.py.mako  # Шаблон миграций
    └── versions/       # Файлы миграций
        └── 462923d90342_skill_added.py
```

## Ключевые моменты

### Безопасность
- Файлы `.env` исключены из версионного контроля
- Чувствительная информация хранится в переменных окружения
- База данных исключена из Git

### Лучшие практики
- Использование описательных сообщений для миграций
- Правильная структура проекта
- Конфигурация через переменные окружения
- Исключение ненужных файлов из версионного контроля

### Автоматизация
- Автогенерация миграций на основе изменений моделей
- Автоматическое применение миграций
- Загрузка конфигурации из файлов окружения

## Команды для работы с миграциями

```bash
# Создание новой миграции
alembic revision --autogenerate -m "описание изменений"

# Применение всех миграций
alembic upgrade head

# Откат к предыдущей миграции
alembic downgrade -1

# Просмотр истории миграций
alembic history

# Проверка текущего состояния
alembic current
```