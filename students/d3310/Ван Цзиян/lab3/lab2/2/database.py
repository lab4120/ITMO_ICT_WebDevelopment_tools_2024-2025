import psycopg2
import psycopg2.extras
from config import DB_CONFIG
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Менеджер базы данных для работы с PostgreSQL"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """
        Подключение к базе данных PostgreSQL
        
        Returns:
            bool: Успешность подключения
        """
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            logger.info("Подключение к базе данных успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            return False
    
    def create_table(self):
        """Создание таблицы для хранения данных веб-страниц"""
        try:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS web_pages (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                parser_type VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            self.cursor.execute(create_table_sql)
            self.connection.commit()
            logger.info("Таблица данных создана успешно")
        except Exception as e:
            logger.error(f"Ошибка создания таблицы: {e}")
    
    def save_page_data(self, url: str, title: str, parser_type: str) -> bool:
        """
        Сохранение данных веб-страницы в базу данных
        
        Args:
            url: URL веб-страницы
            title: Заголовок страницы
            parser_type: Тип парсера (async/threading/multiprocessing)
            
        Returns:
            bool: Успешность сохранения
        """
        try:
            insert_sql = """
            INSERT INTO web_pages (url, title, parser_type)
            VALUES (%s, %s, %s);
            """
            self.cursor.execute(insert_sql, (url, title, parser_type))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
            return False
    
    def close(self):
        """Закрытие соединения с базой данных"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("Соединение с базой данных закрыто")

# Создание глобального экземпляра менеджера базы данных
db_manager = DatabaseManager()
