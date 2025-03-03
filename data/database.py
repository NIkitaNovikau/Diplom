import pymysql
from pymysql.err import MySQLError
from data.config_db import DB_CONFIG

def create_database_rss():
    """Создаёт базу данных, если её нет."""
    try:
        conn = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"База данных '{DB_CONFIG['database']}' проверена/создана.")
    except MySQLError as e:
        print(f"Ошибка при создании базы данных: {e}")
    finally:
        cursor.close()
        conn.close()

def create_table_rss():
    """Создаёт таблицу news, если её нет."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INT AUTO_INCREMENT PRIMARY KEY,
                source VARCHAR(255),
                title TEXT,
                link VARCHAR(500) UNIQUE,
                pub_date DATETIME,
                description TEXT,
                image_url VARCHAR(500),
                viewed BOOL,
                who TEXT
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
    except MySQLError as e:
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        cursor.close()
        conn.close()

def save_news_rss(source_name, title, link, pub_date, description, image_url):
    """Сохраняет новость в базе данных, избегая дубликатов."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Проверяем, есть ли уже запись с таким же link
        cursor.execute("SELECT id FROM news WHERE link = %s", (link,))
        existing_news = cursor.fetchone()

        if existing_news:
            print(f"Новость с таким link уже существует: {link}")
        else:
            cursor.execute("""
                INSERT INTO news (source, title, link, pub_date, description, image_url, viewed, who)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (source_name, title, link, pub_date, description, image_url, 0, "RSS"))

            conn.commit()
            print(f"Новость '{title}' сохранена в базе данных.")

    except MySQLError as e:
        print(f"Ошибка при сохранении новости: {e}")
    finally:
        cursor.close()
        conn.close()

def get_all_news_rss():
    """Получает данные из MySQL"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id,source, title, link, pub_date, viewed, who FROM news ORDER BY pub_date DESC")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except pymysql.MySQLError as e:
        print("Ошибка при работе с базой данных:", e)
        return []

# Функция для пометки новости как прочитанной в базе данных для RSS
def mark_news_as_viewed_rss(news_id):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Обновляем запись в таблице RSS новостей, где название новости соответствует "title"
        query = "UPDATE news SET viewed = 1 WHERE id = %s"
        cursor.execute(query, (news_id,))

        # Сохраняем изменения
        conn.commit()
        print(f"Новость '{news_id}' успешно помечена как прочитанная в RSS.")
    except pymysql.MySQLError as e:
        print(f"Ошибка при пометке новости '{news_id}' как прочитанной: {e}")
    finally:
        # Закрываем соединение
        conn.close()

