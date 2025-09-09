"""
API эндпоинты асинхронного парсера
Использование Celery для фоновой обработки задач
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from app.tasks.parser_tasks import parse_urls_task, health_check_task
from celery.result import AsyncResult
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class AsyncURLParseRequest(BaseModel):
    """Модель запроса асинхронного парсинга URL"""
    urls: List[str]
    mode: str = "asyncio"  # asyncio, threading, multiprocessing

class TaskStatusResponse(BaseModel):
    """Модель ответа со статусом задачи"""
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    progress: Optional[dict] = None

@router.post("/parse-urls-async", response_model=TaskStatusResponse)
async def parse_urls_async(request: AsyncURLParseRequest):
    """
    Асинхронный парсинг списка URL
    
    Запускает фоновую задачу для парсинга списка URL и немедленно возвращает ID задачи
    Клиент может использовать ID задачи для запроса статуса и результатов
    """
    try:
        # Проверка формата URL
        for url in request.urls:
            if not url.startswith(("http://", "https://")):
                raise HTTPException(
                    status_code=400,
                    detail=f"Неверный формат URL: {url}"
                )
        
        # Запуск задачи Celery
        task = parse_urls_task.delay(
            urls=request.urls,
            mode=request.mode
        )
        
        logger.info(f"Запуск асинхронной задачи парсинга: {task.id}, URLs: {len(request.urls)}")
        
        return TaskStatusResponse(
            task_id=task.id,
            status="PENDING",
            progress={"message": "Задача запущена, обрабатывается..."}
        )
        
    except Exception as e:
        logger.error(f"Ошибка запуска асинхронной задачи: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка запуска асинхронной задачи: {str(e)}"
        )

@router.get("/task-status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Получение статуса задачи
    
    Запрашивает статус выполнения и результат задачи по ID задачи
    """
    try:
        # Получение результата задачи
        task_result = AsyncResult(task_id, app=parse_urls_task.app)
        
        if task_result.state == "PENDING":
            return TaskStatusResponse(
                task_id=task_id,
                status="PENDING",
                progress={"message": "Задача ожидает выполнения..."}
            )
        elif task_result.state == "PROGRESS":
            return TaskStatusResponse(
                task_id=task_id,
                status="PROGRESS",
                progress=task_result.info
            )
        elif task_result.state == "SUCCESS":
            return TaskStatusResponse(
                task_id=task_id,
                status="SUCCESS",
                result=task_result.result
            )
        elif task_result.state == "FAILURE":
            return TaskStatusResponse(
                task_id=task_id,
                status="FAILURE",
                error=str(task_result.info)
            )
        else:
            return TaskStatusResponse(
                task_id=task_id,
                status=task_result.state,
                progress={"message": f"Статус задачи: {task_result.state}"}
            )
            
    except Exception as e:
        logger.error(f"Ошибка запроса статуса задачи: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка запроса статуса задачи: {str(e)}"
        )

@router.post("/health-check-async", response_model=TaskStatusResponse)
async def health_check_async():
    """
    Асинхронная проверка здоровья
    
    Запускает фоновую задачу для проверки состояния здоровья сервиса парсера
    """
    try:
        task = health_check_task.delay()
        
        return TaskStatusResponse(
            task_id=task.id,
            status="PENDING",
            progress={"message": "Задача проверки здоровья запущена..."}
        )
        
    except Exception as e:
        logger.error(f"Ошибка запуска задачи проверки здоровья: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка запуска задачи проверки здоровья: {str(e)}"
        )

@router.get("/celery-stats")
async def get_celery_stats():
    """
    Получение статистики Celery
    
    Возвращает статистическую информацию о воркерах Celery
    """
    try:
        from app.celery_app import celery_app
        
        # Получение активных задач
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        reserved_tasks = inspect.reserved()
        
        return {
            "active_tasks": active_tasks,
            "scheduled_tasks": scheduled_tasks,
            "reserved_tasks": reserved_tasks,
            "workers": list(active_tasks.keys()) if active_tasks else []
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики Celery: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения статистики: {str(e)}"
        )
