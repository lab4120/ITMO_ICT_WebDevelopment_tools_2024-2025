import multiprocessing
import time
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from multiprocessing import Pool
from database import db_manager
from config import URLS, MULTIPROCESSING_WORKERS
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
        success = db_manager.save_page_data(url, title_text, "multiprocessing")
        
        # Вывод результата на экран
        if success:
            print(f"[multiprocessing] {url} -> {title_text}")
        else:
            print(f"[multiprocessing] {url} -> ошибка сохранения")
            
        return success
        
    except Exception as e:
        logger.error(f"Ошибка парсинга {url}: {e}")
        print(f"[multiprocessing] {url} -> ошибка парсинга: {e}")
        return False

def main():
    """Главная функция"""
    print("=== Многопроцессный парсер веб-страниц ===")
    start_time = time.time()
    
    # Подключение к базе данных
    if not db_manager.connect():
        print("Не удалось подключиться к базе данных, выход из программы")
        return
    
    # Создание таблицы данных
    db_manager.create_table()
    
    print(f"Использование {MULTIPROCESSING_WORKERS} рабочих процессов для обработки {len(URLS)} URL")
    
    # Использование Pool для управления пулом процессов
    with Pool(processes=MULTIPROCESSING_WORKERS) as pool:
        # Неупорядоченное выполнение для повышения эффективности
        results = list(pool.imap_unordered(parse_and_save, URLS))
    
    # Расчет времени выполнения
    execution_time = time.time() - start_time
    
    # Подсчет успешных и неудачных запросов
    successful = sum(1 for result in results if result is True)
    failed = len(results) - successful
    
    print(f"[multiprocessing] Завершено {len(URLS)} URL, успешно {successful}, неудачно {failed}")
    print(f"[multiprocessing] Общее время {execution_time:.2f}s")
    
    # Закрытие соединения с базой данных
    db_manager.close()

if __name__ == "__main__":
    # Поддержка заморозки для Windows
    multiprocessing.freeze_support()
    main()
