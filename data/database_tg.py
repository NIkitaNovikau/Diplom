import mysql.connector
import re
from data.config import db_config

# Функция очистки текста
def clean_text_tg(text):
    return re.sub(r'\[.*?\]\(.*?\)', '', text).strip()


# Функция для создания базы данных (если её нет)
def create_database_tg():
    conn = mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        port=db_config["port"]
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS tgnews")  # Создание БД
    conn.commit()
    cursor.close()
    conn.close()


# Функция для создания таблицы (если её нет)
def create_table_tg():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telegram_posts (
            id INT AUTO_INCREMENT PRIMARY KEY,  -- Уникальный ID записи
            source VARCHAR(50),  -- Источник
            post_time DATETIME,
            text TEXT,
            photo LONGBLOB,
            post_link VARCHAR(255)  -- Ссылка на пост
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def post_exists_tg(post_time, text, post_link):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Проверяем, есть ли уже запись с таким же post_link
    cursor.execute("""
        SELECT id, text FROM telegram_posts 
        WHERE post_link = %s
    """, (post_link,))

    results = cursor.fetchall()

    if results:
        # Если запись с таким post_link уже существует
        for row in results:
            if row[1] is None or row[1] == "":
                # Если текст пустой, обновляем его
                if text:
                    cursor.execute("UPDATE telegram_posts SET text = %s WHERE id = %s", (text, row[0]))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return True
            else:
                # Если текст уже есть, пропускаем
                cursor.close()
                conn.close()
                return True
    else:
        # Если записи с таким post_link нет, проверяем по post_time
        cursor.execute("""
            SELECT id, text FROM telegram_posts 
            WHERE post_time = %s
        """, (post_time,))

        results = cursor.fetchall()

        if results:
            # Если запись с таким post_time уже существует
            for row in results:
                if row[1] is None or row[1] == "":
                    # Если текст пустой, обновляем его
                    if text:
                        cursor.execute("UPDATE telegram_posts SET text = %s WHERE id = %s", (text, row[0]))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        return True
                else:
                    # Если текст уже есть, пропускаем
                    cursor.close()
                    conn.close()
                    return True
        else:
            # Если записи с таким post_time нет, и текст пустой, пропускаем
            if not text:
                cursor.close()
                conn.close()
                return True

    cursor.close()
    conn.close()
    return False  # Записи нет, но новая запись имеет текст — можно сохранять


# Функция сохранения данных в БД
def save_to_db_tg(post_time, text, post_link, source, photo_data=None):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = """
        INSERT INTO telegram_posts (post_time, text, post_link, source, photo)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (post_time, text, post_link, source, photo_data))
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id
