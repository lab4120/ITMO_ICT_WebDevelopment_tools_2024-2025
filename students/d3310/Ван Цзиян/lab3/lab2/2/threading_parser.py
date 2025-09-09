import threading
import time
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from concurrent.futures import ThreadPoolExecutor
from database import db_manager
from config import URLS, THREADING_WORKERS
import logging
import warnings
from urllib.parse import urlparse

# Игнорировать предупреждения XML парсинга
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_and_save(url: str) -> bool:
    """
    Парсинг указанного URL и сохранение в базу данных
    
    Args:
        url: URL веб-страницы для парсинга
        
    Returns:
        bool: Успешность парсинга и сохранения
    """
    try:
        # Отправка HTTP-запроса
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Единый HTML парсер, игнорировать XML предупреждения
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        
        if title:
            title_text = title.get_text().strip()
        else:
            # Для страниц без title использовать путь URL как заголовок
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            if path:
                title_text = f"{parsed_url.netloc} - {path}"
            else:
                title_text = f"{parsed_url.netloc} - главная"
        
        # Сохранение в базу данных
        success = db_manager.save_page_data(url, title_text, "threading")
        
        # Вывод результата на экран
        if success:
            print(f"[threading] {url} -> {title_text}")
        else:
            print(f"[threading] {url} -> ошибка сохранения")
            
        return success
        
    except Exception as e:
        logger.error(f"Ошибка парсинга {url}: {e}")
        print(f"[threading] {url} -> ошибка парсинга: {e}")
        return False

def worker(urls: list):
    """
    Функция рабочего потока, обработка группы URL
    
    Args:
        urls: Список URL для обработки
    """
    for url in urls:
        parse_and_save(url)

def main():
    """Главная функция"""
    print("=== Многопоточный парсер веб-страниц ===")
    start_time = time.time()
    
    # Подключение к базе данных
    if not db_manager.connect():
        print("Не удалось подключиться к базе данных, выход из программы")
        return
    
    # Создание таблицы данных
    db_manager.create_table()
    
    # Разделение списка URL на равные части
    chunk_size = len(URLS) // THREADING_WORKERS
    if len(URLS) % THREADING_WORKERS != 0:
        chunk_size += 1
    
    url_chunks = [URLS[i:i + chunk_size] for i in range(0, len(URLS), chunk_size)]
    
    print(f"Использование {THREADING_WORKERS} рабочих потоков для обработки {len(URLS)} URL")
    
    # Использование ThreadPoolExecutor для управления пулом потоков
    with ThreadPoolExecutor(max_workers=THREADING_WORKERS) as executor:
        # Отправка всех задач
        futures = [executor.submit(worker, chunk) for chunk in url_chunks]
        
        # Ожидание завершения всех задач
        for future in futures:
            future.result()
    
    # Расчет времени выполнения
    execution_time = time.time() - start_time
    
    print(f"[threading] Завершено {len(URLS)} URL, время {execution_time:.2f}s")
    
    # Закрытие соединения с базой данных
    db_manager.close()

if __name__ == "__main__":
    main()
