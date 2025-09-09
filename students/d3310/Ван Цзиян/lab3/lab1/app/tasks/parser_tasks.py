"""
Определения задач Celery
Для асинхронной обработки задач парсинга URL
"""
import asyncio
import httpx
from typing import List, Dict, Any
from celery import current_task
from app.celery_app import celery_app
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="parse_urls_async")
def parse_urls_task(self, urls: List[str], mode: str = "asyncio") -> Dict[str, Any]:
    """
    Задача асинхронного парсинга списка URL
    
    Args:
        urls: Список URL для парсинга
        mode: Режим парсинга (asyncio, threading, multiprocessing)
    
    Returns:
        Словарь с результатами парсинга
    """
    try:
        # Обновление состояния задачи
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": len(urls), "status": "Начинаем парсинг..."}
        )
        
        # Вызов сервиса парсера
        result = call_parser_service(urls, mode)
        
        return {
            "task_id": self.request.id,
            "status": "SUCCESS",
            "result": result,
            "urls_count": len(urls),
            "mode": mode
        }
        
    except Exception as exc:
        logger.error(f"Ошибка выполнения задачи: {exc}")
        raise exc

def call_parser_service(urls: List[str], mode: str) -> Dict[str, Any]:
    """
    Вызов сервиса парсера
    
    Args:
        urls: Список URL
        mode: Режим парсинга
    
    Returns:
        Результат парсинга
    """
    import requests
    
    parser_url = f"{settings.PARSER_URL}/parse-urls"
    
    payload = {
        "urls": urls,
        "mode": mode
    }
    
    try:
        response = requests.post(
            parser_url,
            json=payload,
            timeout=300  # 5 минут таймаут
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка вызова сервиса парсера: {e}")
        raise Exception(f"Ошибка вызова сервиса парсера: {str(e)}")

@celery_app.task(name="health_check")
def health_check_task() -> Dict[str, Any]:
    """
    Задача проверки здоровья системы
    """
    try:
        import requests
        response = requests.get(f"{settings.PARSER_URL}/health", timeout=10)
        response.raise_for_status()
        return {"status": "healthy", "response": response.json()}
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        return {"status": "unhealthy", "error": str(e)}
