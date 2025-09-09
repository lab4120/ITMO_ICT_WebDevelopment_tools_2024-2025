# Создание Dockerfile

## Обзор

Dockerfile - это текстовый файл, содержащий инструкции для создания Docker образа. В данной лабораторной работе мы создадим Dockerfile для упаковки FastAPI приложения и парсера в контейнеры.

## Зачем нужен Dockerfile?

**Преимущества контейнеризации**:
- **Консистентность среды**: Одинаковая среда выполнения на всех машинах
- **Упрощение развертывания**: Один образ работает везде
- **Изоляция**: Приложение работает в изолированной среде
- **Масштабируемость**: Легкое масштабирование приложения

## Структура Dockerfile

### Базовый Dockerfile для FastAPI

```dockerfile
# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Объяснение инструкций

**FROM python:3.11-slim**
- Использует официальный Python образ версии 3.11
- `slim` версия содержит только необходимые компоненты

**WORKDIR /app**
- Устанавливает рабочую директорию внутри контейнера
- Все последующие команды выполняются в этой директории

**RUN apt-get update && apt-get install -y gcc**
- Обновляет список пакетов
- Устанавливает компилятор gcc для сборки Python пакетов
- `&& rm -rf /var/lib/apt/lists/*` очищает кэш пакетов

**COPY requirements.txt .**
- Копирует файл зависимостей в контейнер
- Делается отдельно для оптимизации кэширования Docker

**RUN pip install --no-cache-dir -r requirements.txt**
- Устанавливает Python зависимости
- `--no-cache-dir` не сохраняет кэш pip

**COPY . .**
- Копирует весь исходный код в контейнер
- Выполняется после установки зависимостей для оптимизации

**RUN useradd --create-home --shell /bin/bash app**
- Создает пользователя для безопасности
- Избегает запуска приложения от root

**ENV PYTHONPATH=/app**
- Устанавливает переменную окружения для Python
- Позволяет импортировать модули из корневой директории

**EXPOSE 8000**
- Документирует порт, который будет использоваться
- Не открывает порт автоматически

**CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]**
- Определяет команду запуска контейнера
- Запускает FastAPI сервер на всех интерфейсах

## Оптимизированный Dockerfile

### Многоэтапная сборка

```dockerfile
# Этап сборки
FROM python:3.11-slim as builder

WORKDIR /app

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Финальный этап
FROM python:3.11-slim

WORKDIR /app

# Копирование установленных пакетов из builder
COPY --from=builder /root/.local /root/.local

# Копирование исходного кода
COPY . .

# Создание пользователя
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Настройка переменных окружения
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Преимущества многоэтапной сборки

- **Меньший размер образа**: Исключаются временные файлы сборки
- **Безопасность**: Нет компиляторов в финальном образе
- **Производительность**: Быстрее загрузка и развертывание

## Dockerfile для парсера

### Отдельный Dockerfile для парсера

```dockerfile
# Dockerfile для парсера
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание пользователя
RUN useradd --create-home --shell /bin/bash parser
RUN chown -R parser:parser /app
USER parser

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открытие порта для парсера
EXPOSE 8001

# Команда запуска парсера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## Создание requirements.txt

### Файл зависимостей

```txt
# requirements.txt
fastapi==0.115.13
uvicorn==0.34.0
sqlalchemy==2.0.35
psycopg2-binary==2.9.10
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
python-multipart==0.0.9
pydantic==2.9.2
jinja2==3.1.5
httpx==0.28.1
sqlmodel==0.0.20
email-validator==2.3.0
celery==5.3.4
redis==5.0.1
```

### Объяснение зависимостей

- **fastapi**: Основной веб-фреймворк
- **uvicorn**: ASGI сервер для запуска FastAPI
- **sqlalchemy**: ORM для работы с базой данных
- **psycopg2-binary**: PostgreSQL драйвер
- **python-jose**: JWT токены для аутентификации
- **passlib**: Хеширование паролей
- **httpx**: HTTP клиент для парсинга
- **celery**: Асинхронная очередь задач
- **redis**: Клиент Redis

## Сборка и тестирование образа

### Сборка образа

```bash
# Сборка образа
docker build -t lab3-api .

# Сборка с тегом версии
docker build -t lab3-api:v1.0 .

# Сборка без кэша
docker build --no-cache -t lab3-api .
```

### Тестирование образа

```bash
# Запуск контейнера
docker run -d -p 8000:8000 --name test-api lab3-api

# Проверка статуса
docker ps

# Проверка логов
docker logs test-api

# Тестирование API
curl http://localhost:8000/health

# Остановка и удаление
docker stop test-api
docker rm test-api
```

## Лучшие практики

### 1. Оптимизация слоев

```dockerfile
# Плохо - каждый COPY создает новый слой
COPY file1.txt .
COPY file2.txt .
COPY file3.txt .

# Хорошо - один слой
COPY file1.txt file2.txt file3.txt .
```

### 2. Использование .dockerignore

```dockerignore
# .dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

.DS_Store
.vscode
.idea
```

### 3. Безопасность

```dockerfile
# Создание непривилегированного пользователя
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Не запускать от root
# USER root  # Избегать этого
```

### 4. Кэширование зависимостей

```dockerfile
# Копировать requirements.txt отдельно
COPY requirements.txt .

# Установить зависимости
RUN pip install -r requirements.txt

# Затем копировать код
COPY . .
```

## Отладка Dockerfile

### Проблемы и решения

**Проблема**: Ошибка при установке зависимостей
```bash
# Решение: Проверить requirements.txt
pip install -r requirements.txt
```

**Проблема**: Большой размер образа
```bash
# Решение: Использовать многоэтапную сборку
docker build --target builder .
```

**Проблема**: Медленная сборка
```bash
# Решение: Оптимизировать порядок инструкций
# Сначала зависимости, потом код
```

### Полезные команды

```bash
# Интерактивная отладка
docker run -it --rm python:3.11-slim bash

# Проверка размера образа
docker images lab3-api

# Анализ слоев
docker history lab3-api

# Проверка содержимого образа
docker run --rm lab3-api ls -la /app
```

## Интеграция с Docker Compose

### Использование в docker-compose.yml

```yaml
# docker-compose.yml
services:
  api:
    build:
      context: ./lab1
      dockerfile: Dockerfile
    container_name: lab3-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/appdb
    depends_on:
      - db

  parser:
    build:
      context: ./lab1
      dockerfile: Dockerfile
    container_name: lab3-parser
    ports:
      - "8001:8001"
    environment:
      - PARSER_MODE=standalone
```

### Переменные окружения

```dockerfile
# В Dockerfile
ENV DATABASE_URL=postgresql://postgres:password@db:5432/appdb
ENV REDIS_URL=redis://redis:6379/0
ENV LOG_LEVEL=INFO
```

```yaml
# В docker-compose.yml
environment:
  - DATABASE_URL=${DATABASE_URL}
  - REDIS_URL=${REDIS_URL}
  - LOG_LEVEL=${LOG_LEVEL:-INFO}
```
