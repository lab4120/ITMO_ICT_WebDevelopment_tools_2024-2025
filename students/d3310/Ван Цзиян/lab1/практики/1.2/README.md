# Практика 1.2: Настройка БД, SQLModel и миграции через Alembic

## Описание проекта
Этот проект демонстрирует настройку базы данных PostgreSQL с использованием SQLModel ORM и Alembic для миграций в FastAPI приложении.

## Требования
- Python 3.10+
- PostgreSQL
- pip

## Установка зависимостей
```bash
pip install -r requirements.txt
```

## Настройка базы данных
1. Установите PostgreSQL с официального сайта
2. Создайте базу данных `warriors_db`
3. Убедитесь, что пользователь `postgres` с паролем `123` имеет доступ к базе данных

## Структура проекта
```
├── requirements.txt      # Зависимости проекта
├── connection.py         # Настройка подключения к БД
├── models.py            # Модели SQLModel
├── main.py              # FastAPI приложение
├── alembic/             # Конфигурация миграций
│   ├── env.py           # Настройка Alembic
│   └── versions/        # Файлы миграций
└── alembic.ini          # Конфигурация Alembic
```

## Использование

### 1. Инициализация миграций
```bash
alembic revision --autogenerate -m "Create warriors table"
```

### 2. Применение миграций
```bash
alembic upgrade head
```

### 3. Запуск приложения
```bash
uvicorn main:app --reload
```

## API Endpoints
- `GET /` - Главная страница
- `GET /warriors/` - Получить всех воинов
- `POST /warriors/` - Создать нового воина

## Модель Warrior
- `id` - Уникальный идентификатор
- `name` - Имя воина
- `level` - Уровень (по умолчанию 1)
- `health` - Здоровье (по умолчанию 100)
- `attack` - Атака (по умолчанию 10)
- `defense` - Защита (по умолчанию 5)
