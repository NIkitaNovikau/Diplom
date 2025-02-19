import mysql.connector
from mysql.connector import Error
from data.config import DB_CONFIG

def create_database_rss():
    """Создаёт базу данных, если её нет."""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"База данных '{DB_CONFIG['database']}' проверена/создана.")
    except Error as e:
        print(f"Ошибка при создании базы данных: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def create_table_rss():
    """Создаёт таблицу news, если её нет."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

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
        if not cursor.fetchone():
            cursor.execute('CREATE INDEX idx_news_link ON news (link)')
            print("Индекс idx_news_link создан.")
        else:
            print("Индекс idx_news_link уже существует.")

        conn.commit()
        print("Таблица news проверена/создана.")
    except Error as e:
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def save_news_rss(source_name, title, link, pub_date, description, image_url):
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

"""def get_all_news_rss():
    #Извлекает все новости из базы данных
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

"""