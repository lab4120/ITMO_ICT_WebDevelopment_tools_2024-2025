# Создание эндпоинтов FastAPI для вызова парсера

## Обзор

В данной задаче мы создадим эндпоинты в FastAPI приложении для вызова парсера, работающего в отдельном контейнере. Это позволит интегрировать функциональность парсинга URL в веб-приложение.

## Зачем нужны эндпоинты для парсера?

**Преимущества интеграции**:
- **Единый интерфейс**: Все функции доступны через один API
- **Централизованное управление**: Один сервис управляет всеми операциями
- **Масштабируемость**: Легко добавлять новые функции парсинга
- **Мониторинг**: Централизованное логирование и мониторинг

## Базовая структура FastAPI приложения

### Основной файл приложения

```python
# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from typing import List, Dict, Any
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="Lab3 Parser API",
    description="API для парсинга URL с интеграцией парсера",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL парсера (работает в отдельном контейнере)
PARSER_URL = "http://parser-api:8001"

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "Lab3 Parser API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    try:
        # Проверка доступности парсера
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PARSER_URL}/health", timeout=5.0)
            parser_status = response.status_code == 200
    except Exception as e:
        logger.error(f"Парсер недоступен: {e}")
        parser_status = False
    
    return {
        "status": "healthy",
        "parser_available": parser_status,
        "services": {
            "api": "ok",
            "parser": "ok" if parser_status else "error"
        }
    }
```

## Модели данных

### Pydantic модели для запросов и ответов

```python
# app/schemas/parser.py
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ParseMode(str, Enum):
    """Режимы парсинга"""
    ASYNCIO = "asyncio"
    THREADING = "threading"
    MULTIPROCESSING = "multiprocessing"

class URLParseRequest(BaseModel):
    """Запрос на парсинг URL"""
    urls: List[str] = Field(
        ..., 
        min_items=1, 
        max_items=100,
        description="Список URL для парсинга, максимум 100"
    )
    mode: ParseMode = Field(
        default=ParseMode.ASYNCIO,
        description="Режим парсинга"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "urls": [
                    "https://httpbin.org/html",
                    "https://example.com"
                ],
                "mode": "asyncio"
            }
        }

class ParseResult(BaseModel):
    """Результат парсинга одного URL"""
    url: str
    status_code: Optional[int] = None
    title: Optional[str] = None
    content_length: Optional[int] = None
    success: bool
    error: Optional[str] = None
    processing_time: Optional[float] = None

class URLParseResponse(BaseModel):
    """Ответ на запрос парсинга"""
    mode: str
    total_urls: int
    successful: int
    failed: int
    total_time: float
    results: List[ParseResult]

class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    error: str
    detail: Optional[str] = None
    status_code: int
```

## Синхронный эндпоинт для парсинга

### Прямой вызов парсера

```python
# app/api/v1/parser.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.parser import URLParseRequest, URLParseResponse, ErrorResponse
import httpx
import time
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/parse-urls", response_model=URLParseResponse)
async def parse_urls(request: URLParseRequest):
    """
    Синхронный парсинг URL через вызов парсера
    
    Отправляет запрос парсеру и ждет результат
    """
    try:
        # Валидация URL
        for url in request.urls:
            if not url.startswith(("http://", "https://")):
                raise HTTPException(
                    status_code=400,
                    detail=f"Неверный формат URL: {url}"
                )
        
        logger.info(f"Запуск парсинга {len(request.urls)} URL в режиме {request.mode}")
        
        # Вызов парсера
        async with httpx.AsyncClient(timeout=60.0) as client:
            start_time = time.time()
            
            response = await client.post(
                f"{PARSER_URL}/api/v1/parse-urls",
                json={
                    "urls": request.urls,
                    "mode": request.mode
                }
            )
            
            end_time = time.time()
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ошибка парсера: {response.text}"
                )
            
            result = response.json()
            result["total_time"] = end_time - start_time
            
            logger.info(f"Парсинг завершен за {result['total_time']:.2f} секунд")
            
            return URLParseResponse(**result)
            
    except httpx.TimeoutException:
        logger.error("Таймаут при вызове парсера")
        raise HTTPException(
            status_code=408,
            detail="Таймаут при обработке запроса парсером"
        )
    except httpx.ConnectError:
        logger.error("Не удается подключиться к парсеру")
        raise HTTPException(
            status_code=503,
            detail="Парсер недоступен"
        )
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )
```

## Асинхронный эндпоинт через Celery

### Интеграция с Celery для фоновой обработки

```python
# app/api/v1/async_parser.py
from fastapi import APIRouter, HTTPException
from app.schemas.parser import URLParseRequest
from app.tasks.parser_tasks import parse_urls_task
from celery.result import AsyncResult
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class TaskStatusResponse(BaseModel):
    """Ответ со статусом задачи"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None

@router.post("/parse-urls-async", response_model=TaskStatusResponse)
async def parse_urls_async(request: URLParseRequest):
    """
    Асинхронный парсинг URL через Celery
    
    Запускает задачу в фоновом режиме и возвращает task_id
    """
    try:
        # Валидация URL
        for url in request.urls:
            if not url.startswith(("http://", "https://")):
                raise HTTPException(
                    status_code=400,
                    detail=f"Неверный формат URL: {url}"
                )
        
        logger.info(f"Запуск асинхронного парсинга {len(request.urls)} URL")
        
        # Запуск Celery задачи
        task = parse_urls_task.delay(request.urls, request.mode)
        
        logger.info(f"Задача запущена с ID: {task.id}")
        
        return TaskStatusResponse(
            task_id=task.id,
            status="PENDING",
            result=None,
            error=None,
            progress=None
        )
        
    except Exception as e:
        logger.error(f"Ошибка при запуске задачи: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось запустить задачу: {str(e)}"
        )

@router.get("/task-status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Получение статуса задачи
    
    Возвращает текущий статус и результат выполнения задачи
    """
    try:
        # Получение результата задачи
        result = AsyncResult(task_id, app=parse_urls_task.app)
        
        response = TaskStatusResponse(
            task_id=task_id,
            status=result.status
        )
        
        # Обработка различных состояний задачи
        if result.status == "SUCCESS":
            response.result = result.result
            if isinstance(result.result, dict) and "progress" in result.result:
                response.progress = result.result["progress"]
        elif result.status == "FAILURE":
            response.error = str(result.info)
        elif result.status == "PROGRESS":
            response.progress = result.info
        elif result.status == "PENDING":
            response.progress = {"status": "Задача ожидает выполнения..."}
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка при получении статуса задачи: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось получить статус задачи: {str(e)}"
        )
```

## Интеграция с парсером

### HTTP клиент для вызова парсера

```python
# app/core/parser_client.py
import httpx
import asyncio
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ParserClient:
    """Клиент для взаимодействия с парсером"""
    
    def __init__(self, parser_url: str = "http://parser-api:8001"):
        self.parser_url = parser_url
        self.timeout = httpx.Timeout(60.0)
    
    async def parse_urls(self, urls: List[str], mode: str = "asyncio") -> Dict[str, Any]:
        """
        Синхронный вызов парсера
        
        Args:
            urls: Список URL для парсинга
            mode: Режим парсинга
            
        Returns:
            Результат парсинга
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.parser_url}/api/v1/parse-urls",
                    json={
                        "urls": urls,
                        "mode": mode
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ошибка парсера: {response.text}")
                
                return response.json()
                
        except httpx.TimeoutException:
            raise Exception("Таймаут при вызове парсера")
        except httpx.ConnectError:
            raise Exception("Парсер недоступен")
        except Exception as e:
            raise Exception(f"Ошибка при вызове парсера: {str(e)}")
    
    async def health_check(self) -> bool:
        """Проверка доступности парсера"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.parser_url}/health")
                return response.status_code == 200
        except Exception:
            return False

# Глобальный экземпляр клиента
parser_client = ParserClient()
```

## Обработка ошибок

### Кастомные исключения

```python
# app/core/exceptions.py
class ParserException(Exception):
    """Базовое исключение парсера"""
    pass

class ParserTimeoutException(ParserException):
    """Таймаут парсера"""
    pass

class ParserUnavailableException(ParserException):
    """Парсер недоступен"""
    pass

class InvalidURLException(ParserException):
    """Неверный URL"""
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Неверный URL: {url}")
```

### Обработчики ошибок

```python
# app/main.py
from app.core.exceptions import (
    ParserException, 
    ParserTimeoutException, 
    ParserUnavailableException,
    InvalidURLException
)

@app.exception_handler(ParserTimeoutException)
async def parser_timeout_handler(request: Request, exc: ParserTimeoutException):
    return JSONResponse(
        status_code=408,
        content={"error": "Таймаут парсера", "detail": str(exc)}
    )

@app.exception_handler(ParserUnavailableException)
async def parser_unavailable_handler(request: Request, exc: ParserUnavailableException):
    return JSONResponse(
        status_code=503,
        content={"error": "Парсер недоступен", "detail": str(exc)}
    )

@app.exception_handler(InvalidURLException)
async def invalid_url_handler(request: Request, exc: InvalidURLException):
    return JSONResponse(
        status_code=400,
        content={"error": "Неверный URL", "detail": str(exc)}
    )
```

## Тестирование эндпоинтов

### Примеры запросов

**Синхронный парсинг**:
```bash
curl -X POST "http://localhost:8000/api/v1/parser/parse-urls" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://httpbin.org/html", "https://example.com"],
    "mode": "asyncio"
  }'
```

**Асинхронный парсинг**:
```bash
# Запуск задачи
curl -X POST "http://localhost:8000/api/v1/async-parser/parse-urls-async" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://httpbin.org/html", "https://example.com"],
    "mode": "asyncio"
  }'

# Проверка статуса (используйте task_id из предыдущего ответа)
curl -X GET "http://localhost:8000/api/v1/async-parser/task-status/{task_id}"
```

### Python клиент для тестирования

```python
# test_client.py
import httpx
import asyncio
import time

async def test_sync_parsing():
    """Тест синхронного парсинга"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/parser/parse-urls",
            json={
                "urls": ["https://httpbin.org/html", "https://example.com"],
                "mode": "asyncio"
            }
        )
        
        print(f"Статус: {response.status_code}")
        print(f"Результат: {response.json()}")

async def test_async_parsing():
    """Тест асинхронного парсинга"""
    async with httpx.AsyncClient() as client:
        # Запуск задачи
        response = await client.post(
            "http://localhost:8000/api/v1/async-parser/parse-urls-async",
            json={
                "urls": ["https://httpbin.org/html", "https://example.com"],
                "mode": "asyncio"
            }
        )
        
        task_data = response.json()
        task_id = task_data["task_id"]
        print(f"Задача запущена: {task_id}")
        
        # Ожидание завершения
        while True:
            status_response = await client.get(
                f"http://localhost:8000/api/v1/async-parser/task-status/{task_id}"
            )
            
            status_data = status_response.json()
            print(f"Статус: {status_data['status']}")
            
            if status_data["status"] in ["SUCCESS", "FAILURE"]:
                print(f"Результат: {status_data}")
                break
            
            await asyncio.sleep(2)

# Запуск тестов
if __name__ == "__main__":
    asyncio.run(test_sync_parsing())
    asyncio.run(test_async_parsing())
```

## Мониторинг и логирование

### Настройка логирования

```python
# app/core/logging.py
import logging
import sys
from datetime import datetime

def setup_logging():
    """Настройка логирования"""
    
    # Создание форматтера
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Файловый обработчик
    file_handler = logging.FileHandler('logs/api.log')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    return root_logger

# Инициализация логирования
logger = setup_logging()
```

### Метрики производительности

```python
# app/core/metrics.py
import time
from functools import wraps

def track_execution_time(func):
    """Декоратор для отслеживания времени выполнения"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(
            f"Функция {func.__name__} выполнена за {end_time - start_time:.2f} секунд"
        )
        
        return result
    return wrapper

# Использование декоратора
@track_execution_time
async def parse_urls(request: URLParseRequest):
    # Логика парсинга
    pass
```

## Интеграция с Docker Compose

### Конфигурация в docker-compose.yml

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
      - PARSER_URL=http://parser-api:8001
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - parser-api
      - redis
    networks:
      - app-network

  parser-api:
    build:
      context: ./lab1
      dockerfile: Dockerfile
    container_name: lab3-parser-api
    ports:
      - "8001:8001"
    environment:
      - PARSER_MODE=standalone
    networks:
      - app-network
```

### Переменные окружения

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PARSER_URL: str = "http://parser-api:8001"
    REDIS_URL: str = "redis://redis:6379/0"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
```
