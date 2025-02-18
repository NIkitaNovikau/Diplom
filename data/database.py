import mysql.connector
from mysql.connector import Error

# Конфигурация подключения к MySQL
DB_CONFIG = {
    "host": "localhost",  #для докера нужен host.docker.internal
    "user": "root",
    "password": "1111",
    "database": "news",  # Имя базы данных
    "port": "3306"
}

def create_db():
    """Создаёт базу данных и таблицу для хранения новостей, если их нет."""
    try:

        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        cursor = conn.cursor()

        # Создаём базу данных, если её нет
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"База данных '{DB_CONFIG['database']}' проверена/создана.")

        cursor.close()
        conn.close()

        # Теперь подключаемся с базой
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Создаём таблицу, если её нет
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS news (
                id INT AUTO_INCREMENT PRIMARY KEY,
                source VARCHAR(255),
                title TEXT,
                link VARCHAR(500) UNIQUE,
                pub_date DATETIME,
                description TEXT,
                image_url VARCHAR(500)
            )
        ''')

        # Проверяем, существует ли индекс
        cursor.execute("SHOW INDEX FROM news WHERE Key_name = 'idx_news_link'")
        index_exists = cursor.fetchone()

        # Если индекс не существует, создаём его
        if not index_exists:
            cursor.execute('CREATE INDEX idx_news_link ON news (link)')
            print("Индекс idx_news_link создан.")
        else:
            print("Индекс idx_news_link уже существует.")

        conn.commit()
        print("Таблица news проверена/создана.")

    except Error as e:
        print(f"Ошибка при создании базы данных или таблицы: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def save_news(source_name, title, link, pub_date, description, image_url):
    """Сохраняет новость в базе данных, избегая дубликатов."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Проверяем, есть ли уже запись с таким же link
        cursor.execute("SELECT id FROM news WHERE link = %s", (link,))
        existing_news = cursor.fetchone()

        if existing_news:
            print(f"Новость с таким link уже существует: {link}")
        else:
            cursor.execute("""
                INSERT INTO news (source, title, link, pub_date, description, image_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (source_name, title, link, pub_date, description, image_url))

            conn.commit()
            print(f"Новость '{title}' сохранена в базе данных.")

    except Error as e:
        print(f"Ошибка при сохранении новости: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_all_news():
    """Извлекает все новости из базы данных."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT source, title, link, pub_date, description, image_url FROM news")
        news = cursor.fetchall()

        return news

    except Error as e:
        print(f"Ошибка при получении данных: {e}")
        return []

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

