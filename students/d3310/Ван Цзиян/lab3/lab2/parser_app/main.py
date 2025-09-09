from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import time
import aiohttp
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from urllib.parse import urlparse
import warnings
from typing import List, Dict, Any
import logging
import concurrent.futures
import multiprocessing

# Игнорирование предупреждений XML парсинга
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Parser Service", version="1.0.0")


class URLParseRequest(BaseModel):
    urls: List[str]
    parser_type: str = "asyncio"  # asyncio, threading, multiprocessing
    timeout: int = 10

class ParsedResult(BaseModel):
    url: str
    title: str
    success: bool
    error: str = None

class ParseResponse(BaseModel):
    results: List[ParsedResult]
    total_urls: int
    successful: int
    failed: int
    elapsed_sec: float
    parser_type: str

@app.get("/")
async def root():
    """Корневой путь сервиса парсера"""
    return {
        "service": "Parser Service",
        "version": "1.0.0",
        "description": "Сервис парсинга URL",
        "endpoints": {
            "health": "/health",
            "parse_urls": "/parse-urls",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


async def parse_url_async(url: str, session: aiohttp.ClientSession, timeout: int = 10) -> ParsedResult:
    """Асинхронный парсинг одного URL"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
            response.raise_for_status()
            content = await response.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        title = soup.find('title')
        
        if title:
            title_text = title.get_text().strip()
        else:
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            if path:
                title_text = f"{parsed_url.netloc} - {path}"
            else:
                title_text = f"{parsed_url.netloc} - Главная страница"
        
        return ParsedResult(url=url, title=title_text, success=True)
        
    except Exception as e:
        logger.error(f"Ошибка парсинга URL {url}: {e}")
        return ParsedResult(url=url, title="", success=False, error=str(e))

def parse_url_sync(url: str, timeout: int = 10) -> ParsedResult:
    """Синхронный парсинг одного URL"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        
        if title:
            title_text = title.get_text().strip()
        else:
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            if path:
                title_text = f"{parsed_url.netloc} - {path}"
            else:
                title_text = f"{parsed_url.netloc} - Главная страница"
        
        return ParsedResult(url=url, title=title_text, success=True)
        
    except Exception as e:
        logger.error(f"Ошибка парсинга URL {url}: {e}")
        return ParsedResult(url=url, title="", success=False, error=str(e))

@app.post("/parse-urls", response_model=ParseResponse)
async def parse_urls(req: URLParseRequest) -> ParseResponse:
    """Парсинг списка URL"""
    start_time = time.time()
    
    if not req.urls:
        raise HTTPException(status_code=400, detail="Список URL не может быть пустым")
    
    results = []
    
    if req.parser_type == "asyncio":
        # Асинхронный парсинг
        semaphore = asyncio.Semaphore(10)  # Ограничение количества одновременных запросов
        
        async def parse_with_semaphore(url):
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    return await parse_url_async(url, session, req.timeout)
        
        tasks = [parse_with_semaphore(url) for url in req.urls]
        results = await asyncio.gather(*tasks)
        
    elif req.parser_type == "threading":
        # Многопоточный парсинг
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(parse_url_sync, url, req.timeout) for url in req.urls]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
    elif req.parser_type == "multiprocessing":
        # Многопроцессный парсинг
        with multiprocessing.Pool(processes=min(4, multiprocessing.cpu_count())) as pool:
            results = pool.map(parse_url_sync, req.urls)
            
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемый тип парсера")
    
    elapsed_time = time.time() - start_time
    successful = sum(1 for result in results if result.success)
    failed = len(results) - successful
    
    return ParseResponse(
        results=results,
        total_urls=len(req.urls),
        successful=successful,
        failed=failed,
        elapsed_sec=round(elapsed_time, 6),
        parser_type=req.parser_type
    )


