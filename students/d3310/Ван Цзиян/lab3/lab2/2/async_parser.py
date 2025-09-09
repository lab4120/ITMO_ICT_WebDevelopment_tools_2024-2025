import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from database import db_manager
from config import URLS, ASYNC_CONCURRENCY
import logging
import warnings

# Игнорировать предупреждения XML парсинга
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def parse_and_save(url: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore) -> bool:
    """
    Асинхронный парсинг указанного URL и сохранение в базу данных
    
    Args:
        url: URL веб-страницы для парсинга
        session: aiohttp сессия
        semaphore: семафор для контроля конкурентности
        
    Returns:
        bool: Успешность парсинга и сохранения
    """
    async with semaphore:
        try:
            # Отправка асинхронного HTTP-запроса
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response.raise_for_status()
                content = await response.read()
            
            # Единый HTML парсер, игнорировать XML предупреждения
            soup = BeautifulSoup(content, 'html.parser')
            title = soup.find('title')
            
            if title:
                title_text = title.get_text().strip()
            else:
                # Для страниц без title использовать путь URL как заголовок
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                path = parsed_url.path.strip('/')
                if path:
                    title_text = f"{parsed_url.netloc} - {path}"
                else:
                    title_text = f"{parsed_url.netloc} - главная"
            
            # Сохранение в базу данных
            success = db_manager.save_page_data(url, title_text, "async")
            
            # Вывод результата на экран
            if success:
                print(f"[async] {url} -> {title_text}")
            else:
                print(f"[async] {url} -> ошибка сохранения")
                
            return success
            
        except Exception as e:
            logger.error(f"Ошибка парсинга {url}: {e}")
            print(f"[async] {url} -> ошибка парсинга: {e}")
            return False

async def main():
    """Главная асинхронная функция"""
    print("=== Асинхронный парсер веб-страниц ===")
    start_time = time.time()
    
    # Подключение к базе данных
    if not db_manager.connect():
        print("Не удалось подключиться к базе данных, выход из программы")
        return
    
    # Создание таблицы данных
    db_manager.create_table()
    
    print(f"Использование {ASYNC_CONCURRENCY} конкурентных соединений для обработки {len(URLS)} URL")
    
    # Создание семафора для контроля конкурентности
    semaphore = asyncio.Semaphore(ASYNC_CONCURRENCY)
    
    # Создание aiohttp сессии
    connector = aiohttp.TCPConnector(limit=ASYNC_CONCURRENCY)
    timeout = aiohttp.ClientTimeout(total=10)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Создание всех задач
        tasks = [
            parse_and_save(url, session, semaphore) 
            for url in URLS
        ]
        
        # Ожидание завершения всех задач
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Расчет времени выполнения
    execution_time = time.time() - start_time
    
    # Подсчет успешных и неудачных запросов
    successful = sum(1 for result in results if result is True)
    failed = len(results) - successful
    
    print(f"[async] Завершено {len(URLS)} URL, успешно {successful}, неудачно {failed}")
    print(f"[async] Общее время {execution_time:.2f}s")
    
    # Закрытие соединения с базой данных
    db_manager.close()

if __name__ == "__main__":
    # Запуск асинхронной главной функции
    asyncio.run(main())
