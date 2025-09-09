# Настройка Redis

## Обзор

Redis (Remote Dictionary Server) - это высокопроизводительное in-memory хранилище данных, которое используется в нашей лабораторной работе как брокер сообщений для Celery и хранилище результатов задач.

## Зачем нужен Redis?

**Преимущества Redis**:
- **Высокая производительность**: Данные хранятся в памяти
- **Надежность**: Поддержка персистентности данных
- **Гибкость**: Различные типы данных (строки, списки, множества, хеши)
- **Масштабируемость**: Поддержка кластеризации и репликации

## Установка и конфигурация

### Docker Compose конфигурация

```yaml
# docker-compose.yml
services:
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
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
```

### Объяснение параметров

**image: redis:7-alpine**:
- Использует Redis версии 7
- Alpine Linux для минимального размера образа

**--appendonly yes**:
- Включает AOF (Append Only File) для персистентности
- Обеспечивает сохранность данных при перезапуске

**--maxmemory 512mb**:
- Ограничивает использование памяти до 512MB
- Предотвращает переполнение памяти

**--maxmemory-policy allkeys-lru**:
- Политика вытеснения при достижении лимита памяти
- Удаляет наименее используемые ключи

**healthcheck**:
- Проверка здоровья сервиса каждые 10 секунд
- Команда `redis-cli ping` для проверки доступности

## Подключение к Redis

### Python клиент Redis

```python
# app/core/redis.py
import redis
from app.core.config import settings
import json
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    """Клиент для работы с Redis"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    def ping(self) -> bool:
        """Проверка подключения к Redis"""
        try:
            return self.redis_client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Сохранение значения в Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.redis_client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis set failed: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Получение значения из Redis"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Попытка десериализации JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Redis get failed: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Удаление ключа из Redis"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete failed: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists failed: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """Установка времени жизни ключа"""
        try:
            return self.redis_client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis expire failed: {e}")
            return False

# Глобальный экземпляр клиента
redis_client = RedisClient()
```

### Конфигурация подключения

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Redis конфигурация
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # Celery Redis конфигурация
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Использование Redis в Celery

### Конфигурация Celery с Redis

```python
# app/celery_app.py
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "lab3_parser",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.parser_tasks"]
)

# Redis специфичные настройки
celery_app.conf.update(
    # Настройки брокера
    broker_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
        'retry_policy': {
            'timeout': 5.0
        }
    },
    
    # Настройки результата
    result_backend_transport_options={
        'master_name': 'mymaster',
    },
    
    # Сериализация
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Время жизни результатов
    result_expires=3600,  # 1 час
    result_persistent=True,
    
    # Настройки задач
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)
```

### Очереди и маршрутизация

```python
# Настройка очередей
celery_app.conf.task_routes = {
    'app.tasks.parser_tasks.parse_urls_task': {'queue': 'parser_queue'},
    'app.tasks.parser_tasks.health_check_task': {'queue': 'health_queue'},
}

# Определение очередей
celery_app.conf.task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'parser_queue': {
        'exchange': 'parser',
        'routing_key': 'parser',
    },
    'health_queue': {
        'exchange': 'health',
        'routing_key': 'health',
    },
}
```

## Кэширование в Redis

### Кэш для результатов парсинга

```python
# app/core/cache.py
from app.core.redis import redis_client
from typing import Any, Optional
import hashlib
import json

class CacheManager:
    """Менеджер кэширования"""
    
    def __init__(self, prefix: str = "cache"):
        self.prefix = prefix
    
    def _generate_key(self, data: Any) -> str:
        """Генерация ключа кэша на основе данных"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        hash_obj = hashlib.md5(data_str.encode())
        return f"{self.prefix}:{hash_obj.hexdigest()}"
    
    def get(self, key_data: Any) -> Optional[Any]:
        """Получение из кэша"""
        cache_key = self._generate_key(key_data)
        return redis_client.get(cache_key)
    
    def set(self, key_data: Any, value: Any, expire: int = 3600) -> bool:
        """Сохранение в кэш"""
        cache_key = self._generate_key(key_data)
        return redis_client.set(cache_key, value, expire=expire)
    
    def delete(self, key_data: Any) -> bool:
        """Удаление из кэша"""
        cache_key = self._generate_key(key_data)
        return redis_client.delete(cache_key)
    
    def clear_pattern(self, pattern: str) -> int:
        """Очистка кэша по паттерну"""
        try:
            keys = redis_client.redis_client.keys(f"{self.prefix}:{pattern}")
            if keys:
                return redis_client.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern failed: {e}")
            return 0

# Глобальные экземпляры кэша
url_cache = CacheManager("url_parse")
session_cache = CacheManager("session")
```

### Использование кэша в задачах

```python
# app/tasks/parser_tasks.py
from app.core.cache import url_cache

@celery_app.task(bind=True)
def parse_urls_with_cache(self, urls: List[str], mode: str = "asyncio"):
    """
    Парсинг URL с кэшированием
    """
    results = []
    cached_count = 0
    
    for url in urls:
        # Проверка кэша
        cached_result = url_cache.get(url)
        if cached_result:
            results.append(cached_result)
            cached_count += 1
            continue
        
        # Парсинг URL
        result = parse_single_url(url)
        
        # Сохранение в кэш (1 час)
        url_cache.set(url, result, expire=3600)
        results.append(result)
    
    return {
        "total_urls": len(urls),
        "cached_urls": cached_count,
        "parsed_urls": len(urls) - cached_count,
        "results": results
    }
```

## Сессии и аутентификация

### Redis сессии

```python
# app/core/session.py
from app.core.redis import redis_client
from app.core.cache import session_cache
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class SessionManager:
    """Менеджер сессий"""
    
    def __init__(self, session_timeout: int = 3600):
        self.session_timeout = session_timeout
    
    def create_session(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """Создание новой сессии"""
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        session_cache.set(session_id, session_data, expire=self.session_timeout)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение данных сессии"""
        return session_cache.get(session_id)
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Обновление сессии"""
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        session_data.update(data)
        session_data["last_activity"] = datetime.utcnow().isoformat()
        
        return session_cache.set(session_id, session_data, expire=self.session_timeout)
    
    def delete_session(self, session_id: str) -> bool:
        """Удаление сессии"""
        return session_cache.delete(session_id)
    
    def extend_session(self, session_id: str) -> bool:
        """Продление сессии"""
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        session_data["last_activity"] = datetime.utcnow().isoformat()
        return session_cache.set(session_id, session_data, expire=self.session_timeout)

# Глобальный экземпляр
session_manager = SessionManager()
```

## Мониторинг Redis

### Проверка состояния

```python
# app/api/v1/redis_monitor.py
from fastapi import APIRouter, HTTPException
from app.core.redis import redis_client
from app.core.config import settings
import redis

router = APIRouter()

@router.get("/redis/status")
async def get_redis_status():
    """Получение статуса Redis"""
    try:
        # Проверка подключения
        ping_result = redis_client.ping()
        
        # Получение информации о сервере
        info = redis_client.redis_client.info()
        
        return {
            "status": "healthy" if ping_result else "unhealthy",
            "ping": ping_result,
            "version": info.get("redis_version"),
            "uptime": info.get("uptime_in_seconds"),
            "memory_used": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_commands_processed": info.get("total_commands_processed")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@router.get("/redis/memory")
async def get_redis_memory():
    """Получение информации о памяти Redis"""
    try:
        info = redis_client.redis_client.info("memory")
        
        return {
            "used_memory": info.get("used_memory"),
            "used_memory_human": info.get("used_memory_human"),
            "used_memory_rss": info.get("used_memory_rss"),
            "used_memory_peak": info.get("used_memory_peak"),
            "maxmemory": info.get("maxmemory"),
            "maxmemory_policy": info.get("maxmemory_policy")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis memory error: {str(e)}")

@router.get("/redis/keys")
async def get_redis_keys(pattern: str = "*"):
    """Получение списка ключей Redis"""
    try:
        keys = redis_client.redis_client.keys(pattern)
        return {
            "pattern": pattern,
            "count": len(keys),
            "keys": keys[:100]  # Ограничиваем до 100 ключей
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis keys error: {str(e)}")
```

### Командная строка мониторинга

```bash
# Подключение к Redis CLI
docker compose exec redis redis-cli

# Основные команды мониторинга
INFO                    # Общая информация
INFO memory            # Информация о памяти
INFO clients           # Информация о клиентах
INFO stats             # Статистика
MONITOR                # Мониторинг команд в реальном времени

# Управление ключами
KEYS *                 # Все ключи
KEYS celery:*         # Ключи с префиксом
TTL key_name          # Время жизни ключа
EXPIRE key_name 3600  # Установка времени жизни

# Управление памятью
MEMORY USAGE key_name  # Использование памяти ключом
MEMORY STATS          # Статистика памяти
```

## Производительность и оптимизация

### Настройки производительности

```yaml
# docker-compose.yml оптимизация
redis:
  image: redis:7-alpine
  command: >
    redis-server
    --appendonly yes
    --maxmemory 1gb
    --maxmemory-policy allkeys-lru
    --tcp-keepalive 60
    --timeout 300
    --tcp-backlog 511
    --databases 16
    --save 900 1
    --save 300 10
    --save 60 10000
```

### Оптимизация подключений

```python
# app/core/redis_pool.py
import redis
from app.core.config import settings

class RedisPool:
    """Пул подключений к Redis"""
    
    def __init__(self):
        self.pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            max_connections=20,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            decode_responses=True
        )
        
        self.redis_client = redis.Redis(connection_pool=self.pool)
    
    def get_client(self):
        return self.redis_client

# Глобальный пул подключений
redis_pool = RedisPool()
```

## Безопасность

### Аутентификация Redis

```yaml
# docker-compose.yml с паролем
redis:
  image: redis:7-alpine
  command: redis-server --requirepass your_strong_password
  environment:
    - REDIS_PASSWORD=your_strong_password
```

### Конфигурация с паролем

```python
# app/core/config.py
class Settings(BaseSettings):
    REDIS_PASSWORD: str = "your_strong_password"
    REDIS_URL: str = "redis://:your_strong_password@redis:6379/0"
```

### Ограничение доступа

```yaml
# redis.conf
# Ограничение доступа только к локальным подключениям
bind 127.0.0.1 redis

# Отключение опасных команд
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

## Резервное копирование

### Автоматическое резервное копирование

```bash
#!/bin/bash
# backup_redis.sh

BACKUP_DIR="/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/redis_backup_$DATE.rdb"

# Создание резервной копии
docker compose exec redis redis-cli BGSAVE

# Копирование файла
docker compose cp redis:/data/dump.rdb "$BACKUP_FILE"

# Сжатие
gzip "$BACKUP_FILE"

echo "Backup created: $BACKUP_FILE.gz"
```

### Восстановление из резервной копии

```bash
#!/bin/bash
# restore_redis.sh

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Остановка Redis
docker compose stop redis

# Копирование файла резервной копии
docker compose cp "$BACKUP_FILE" redis:/data/dump.rdb

# Запуск Redis
docker compose start redis

echo "Redis restored from: $BACKUP_FILE"
```

## Тестирование

### Тест подключения к Redis

```python
# tests/test_redis.py
import pytest
from app.core.redis import redis_client

def test_redis_connection():
    """Тест подключения к Redis"""
    assert redis_client.ping() == True

def test_redis_set_get():
    """Тест записи и чтения данных"""
    test_key = "test_key"
    test_value = {"test": "data"}
    
    # Запись
    assert redis_client.set(test_key, test_value) == True
    
    # Чтение
    result = redis_client.get(test_key)
    assert result == test_value
    
    # Очистка
    redis_client.delete(test_key)

def test_redis_expire():
    """Тест истечения времени жизни ключа"""
    test_key = "expire_test"
    test_value = "test_value"
    
    # Запись с истечением через 1 секунду
    redis_client.set(test_key, test_value, expire=1)
    
    # Проверка существования
    assert redis_client.exists(test_key) == True
    
    # Ожидание истечения
    import time
    time.sleep(2)
    
    # Проверка отсутствия
    assert redis_client.exists(test_key) == False
```

### Тест интеграции с Celery

```python
# tests/test_celery_redis.py
import pytest
from app.celery_app import celery_app
from app.tasks.parser_tasks import parse_urls_task

@pytest.mark.celery
def test_celery_redis_integration():
    """Тест интеграции Celery с Redis"""
    
    # Проверка подключения к брокеру
    inspect = celery_app.control.inspect()
    stats = inspect.stats()
    
    assert stats is not None
    
    # Тест создания задачи
    task = parse_urls_task.delay(["https://httpbin.org/html"], "asyncio")
    
    assert task.id is not None
    assert task.status in ["PENDING", "SUCCESS", "FAILURE"]
```
