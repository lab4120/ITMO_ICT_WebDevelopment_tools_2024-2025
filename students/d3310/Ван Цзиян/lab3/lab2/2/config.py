import os
from typing import List

# Конфигурация базы данных
DB_CONFIG = {
    'host': os.getenv('PGHOST', '127.0.0.1'),
    'port': os.getenv('PGPORT', '5432'),
    'user': os.getenv('PGUSER', 'postgres'),
    'password': os.getenv('PGPASSWORD', '221bbs'),
    'database': os.getenv('PGDATABASE', 'postgres'),
    'client_encoding': 'utf8'  # Настройка кодировки
}

# Список URL для парсинга - 10 разнообразных стабильных сайтов с заголовками
URLS = [
    'https://www.python.org/',
    'https://httpbin.org/',
    'https://jsonplaceholder.typicode.com/',
    'https://httpbin.org/xml',
    'https://httpbin.org/links/10',
    'https://httpbin.org/html',
    'https://httpbin.org/forms/post',
    'https://httpbin.org/headers',
    'https://httpbin.org/user-agent',
    'https://httpbin.org/ip'
]

# Конфигурация конкурентности
THREADING_WORKERS = 5
MULTIPROCESSING_WORKERS = min(8, os.cpu_count() - 1) if os.cpu_count() else 4
ASYNC_CONCURRENCY = 10
