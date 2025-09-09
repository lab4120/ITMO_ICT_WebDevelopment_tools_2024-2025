from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from app.core.config import settings
from typing import List, Optional

router = APIRouter()


class URLParseIn(BaseModel):
    urls: List[str]
    parser_type: str = "asyncio"  # asyncio, threading, multiprocessing
    timeout: int = 10


@router.post("/parse-urls")
async def call_url_parser(payload: URLParseIn):
    """Вызов парсера для анализа URL"""
    parser_url = getattr(settings, "PARSER_URL", "http://parser:8001")
    url = f"{parser_url}/parse-urls"
    
    if not payload.urls:
        raise HTTPException(status_code=400, detail="Список URL не может быть пустым")
    
    # Проверка формата URL
    for url_item in payload.urls:
        if not url_item.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail=f"Неверный формат URL: {url_item}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload.model_dump())
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Таймаут сервиса парсера")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Ошибка сервиса парсера: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {exc}")

@router.get("/parser-health")
async def check_parser_health():
    """Проверка состояния здоровья сервиса парсера"""
    parser_url = getattr(settings, "PARSER_URL", "http://parser:8001")
    url = f"{parser_url}/health"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Сервис парсера недоступен: {exc}")
