# Создание Docker Compose файла

## Обзор

Docker Compose - это инструмент для определения и запуска многоконтейнерных Docker приложений. В данной лабораторной работе мы создадим docker-compose.yml файл для управления кластером сервисов, включающим FastAPI приложение, базу данных и парсер.

## Зачем нужен Docker Compose?

**Преимущества Docker Compose**:
- **Упрощение управления**: Один файл для всех сервисов
- **Автоматизация зависимостей**: Автоматический запуск зависимых сервисов
- **Изоляция сети**: Сервисы работают в изолированной сети
- **Консистентность**: Одинаковая конфигурация на всех машинах

## Базовая структура docker-compose.yml

### Минимальная конфигурация

```yaml
# docker-compose.yml
version: '3.8'

services:
  # FastAPI приложение
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

  # База данных PostgreSQL
  db:
    image: postgres:16-alpine
    container_name: lab3-database
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: appdb
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data

  # Парсер
  parser:
    build:
      context: ./lab1
      dockerfile: Dockerfile
    container_name: lab3-parser
    ports:
      - "8001:8001"
    environment:
      - PARSER_MODE=standalone

volumes:
  db_data:
```

### Объяснение структуры

**version: '3.8'**
- Указывает версию формата Docker Compose
- Версия 3.8 поддерживает все современные функции

**services**
- Секция для определения всех сервисов приложения
- Каждый сервис - это отдельный контейнер

**build**
- Указывает, что образ нужно собрать из Dockerfile
- `context` - путь к директории с Dockerfile
- `dockerfile` - имя файла Dockerfile

**container_name**
- Задает имя контейнера
- Полезно для отладки и мониторинга

**ports**
- Маппинг портов между хостом и контейнером
- Формат: "хост:контейнер"

**environment**
- Переменные окружения для контейнера
- Могут быть заданы как список или словарь

**depends_on**
- Указывает зависимости между сервисами
- Сервис запустится только после зависимых сервисов

## Полная конфигурация с Redis и Celery

### Расширенный docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Redis - брокер сообщений для Celery
  redis:
    image: redis:7-alpine
    container_name: lab3-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  # PostgreSQL база данных
  db:
    image: postgres:16-alpine
    container_name: lab3-database
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-221bbs}
      POSTGRES_DB: ${POSTGRES_DB:-appdb}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-appdb}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  # FastAPI приложение
  api:
    build:
      context: ./lab1
      dockerfile: Dockerfile
    container_name: lab3-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-221bbs}@db:5432/${POSTGRES_DB:-appdb}
    depends_on:
      redis:
        condition: service_healthy
      db:
        condition: service_healthy
    networks:
      - app-network
    volumes:
      - ./lab1:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Парсер API
  parser-api:
    build:
      context: ./lab1
      dockerfile: Dockerfile
    container_name: lab3-parser-api
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-221bbs}@db:5432/${POSTGRES_DB:-appdb}
    depends_on:
      redis:
        condition: service_healthy
      db:
        condition: service_healthy
    networks:
      - app-network
    volumes:
      - ./lab1:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

  # Celery Worker
  celery-worker:
    build:
      context: ./lab1
      dockerfile: Dockerfile
    container_name: lab3-celery-worker
    restart: unless-stopped
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-221bbs}@db:5432/${POSTGRES_DB:-appdb}
    depends_on:
      redis:
        condition: service_healthy
      db:
        condition: service_healthy
    networks:
      - app-network
    volumes:
      - ./lab1:/app
    command: celery -A app.celery_app worker --loglevel=info --concurrency=4

  # Celery Beat - планировщик задач
  celery-beat:
    build:
      context: ./lab1
      dockerfile: Dockerfile
    container_name: lab3-celery-beat
    restart: unless-stopped
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-221bbs}@db:5432/${POSTGRES_DB:-appdb}
    depends_on:
      redis:
        condition: service_healthy
      db:
        condition: service_healthy
    networks:
      - app-network
    volumes:
      - ./lab1:/app
    command: celery -A app.celery_app beat --loglevel=info

networks:
  app-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  db_data:
    driver: local
  redis_data:
    driver: local
```

### Объяснение расширенных настроек

**restart: unless-stopped**
- Автоматический перезапуск контейнера при сбое
- Исключает ручную остановку

**healthcheck**
- Проверка здоровья сервиса
- `test` - команда для проверки
- `interval` - интервал проверки
- `timeout` - таймаут команды
- `retries` - количество попыток
- `start_period` - время ожидания перед первой проверкой

**depends_on с condition**
- Запуск только после успешной проверки здоровья
- Гарантирует готовность зависимых сервисов

**networks**
- Создание изолированной сети
- Сервисы могут обращаться друг к другу по имени
- `subnet` - подсеть для контейнеров

**volumes**
- Постоянное хранение данных
- `db_data` - данные PostgreSQL
- `redis_data` - данные Redis

## Переменные окружения

### Создание .env файла

```bash
# .env
# База данных
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=appdb

# Redis
REDIS_URL=redis://redis:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000
PARSER_API_PORT=8001

# Безопасность
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Логирование
LOG_LEVEL=INFO

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Использование переменных в docker-compose.yml

```yaml
# Использование переменных окружения
environment:
  - POSTGRES_USER=${POSTGRES_USER:-postgres}
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-221bbs}
  - POSTGRES_DB=${POSTGRES_DB:-appdb}
  - REDIS_URL=${REDIS_URL:-redis://redis:6379/0}
  - LOG_LEVEL=${LOG_LEVEL:-INFO}
```

**Синтаксис**: `${VARIABLE:-default_value}`
- Если переменная не задана, используется значение по умолчанию

## Управление сервисами

### Основные команды

```bash
# Запуск всех сервисов
docker compose up -d

# Запуск конкретных сервисов
docker compose up -d api db redis

# Остановка всех сервисов
docker compose down

# Остановка с удалением томов
docker compose down -v

# Перезапуск сервиса
docker compose restart api

# Масштабирование сервиса
docker compose up -d --scale celery-worker=3
```

### Мониторинг

```bash
# Статус всех сервисов
docker compose ps

# Логи всех сервисов
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f api

# Использование ресурсов
docker compose top
```

## Конфигурация для разработки

### Настройки для разработки

```yaml
# docker-compose.override.yml (автоматически подключается)
version: '3.8'

services:
  api:
    volumes:
      - ./lab1:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG

  parser-api:
    volumes:
      - ./lab1:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG

  celery-worker:
    volumes:
      - ./lab1:/app
    command: celery -A app.celery_app worker --loglevel=debug --concurrency=2
```

### Отдельная конфигурация для продакшена

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    restart: always
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  celery-worker:
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

**Запуск с продакшен конфигурацией**:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Отладка и решение проблем

### Частые проблемы

**Проблема**: Сервис не запускается
```bash
# Решение: Проверить логи
docker compose logs api

# Проверить статус
docker compose ps
```

**Проблема**: Ошибка подключения к базе данных
```bash
# Решение: Проверить переменные окружения
docker compose exec api env | grep DATABASE

# Проверить доступность базы
docker compose exec db pg_isready -U postgres
```

**Проблема**: Redis недоступен
```bash
# Решение: Проверить Redis
docker compose exec redis redis-cli ping

# Проверить сеть
docker network ls
docker network inspect lab3_app-network
```

### Полезные команды отладки

```bash
# Подключение к контейнеру
docker compose exec api bash

# Проверка переменных окружения
docker compose exec api env

# Проверка сетевых подключений
docker compose exec api netstat -tulpn

# Проверка процессов
docker compose exec api ps aux
```

## Оптимизация производительности

### Настройки ресурсов

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  celery-worker:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Оптимизация образов

```yaml
services:
  api:
    build:
      context: ./lab1
      dockerfile: Dockerfile
      target: production  # Использовать многоэтапную сборку
```

## Безопасность

### Настройки безопасности

```yaml
services:
  db:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password

  api:
    environment:
      SECRET_KEY_FILE: /run/secrets/secret_key
    secrets:
      - secret_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  secret_key:
    file: ./secrets/secret_key.txt
```

### Ограничение доступа

```yaml
services:
  db:
    ports: []  # Не открывать порт наружу
    networks:
      - app-network

  redis:
    ports: []  # Не открывать порт наружу
    networks:
      - app-network
```

## Резервное копирование

### Скрипт резервного копирования

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "Начинаем резервное копирование..."

# Создание директории
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
echo "Резервное копирование PostgreSQL..."
docker compose exec -T db pg_dump -U postgres appdb > $BACKUP_DIR/postgres_backup_$DATE.sql

# Backup Redis
echo "Резервное копирование Redis..."
docker compose exec -T redis redis-cli BGSAVE
docker compose cp redis:/data/dump.rdb $BACKUP_DIR/redis_backup_$DATE.rdb

# Backup конфигурации
echo "Резервное копирование конфигурации..."
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz docker-compose.yml .env

echo "Резервное копирование завершено!"
```
