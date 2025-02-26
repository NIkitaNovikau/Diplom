import pymysql
import re
from data.config_db import db_config

# Функция очистки текста
def clean_text_tg(text):
    return re.sub(r'\[.*?\]\(.*?\)', '', text).strip()


# Функция для создания базы данных (если её нет)
def create_database_tg():
    try:
        conn = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            port=int(db_config["port"])  # Убедимся, что порт - int
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS tgnews")  # Создание БД
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Ошибка при создании базы данных: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Функция для создания таблицы (если её нет)
def create_table_tg():
    try:
        conn = pymysql.connect(**db_config)
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
    except pymysql.MySQLError as e:
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def post_exists_tg(post_time, text, post_link):
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # Проверяем, есть ли уже запись с таким же post_link
        cursor.execute("""
            SELECT id, text FROM telegram_posts 
            WHERE post_link = %s
        """, (post_link,))

        results = cursor.fetchall()

        if results:
            for row in results:
                if not row[1]:  # Если текст пустой, обновляем его
                    if text:
                        cursor.execute("UPDATE telegram_posts SET text = %s WHERE id = %s", (text, row[0]))
                        conn.commit()
                    return True
                return True  # Запись уже есть, пропускаем
        else:
            # Проверяем по post_time
            cursor.execute("""
                SELECT id, text FROM telegram_posts 
                WHERE post_time = %s
            """, (post_time,))

            results = cursor.fetchall()

            if results:
                for row in results:
                    if not row[1]:  # Если текст пустой, обновляем его
                        if text:
                            cursor.execute("UPDATE telegram_posts SET text = %s WHERE id = %s", (text, row[0]))
                            conn.commit()
                        return True
                    return True  # Запись уже есть, пропускаем
            else:
                # Если записи нет, но текст пустой — пропускаем
                if not text:
                    return True

        return False  # Можно сохранять новую запись
    except pymysql.MySQLError as e:
        print(f"Ошибка при проверке записи: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Функция сохранения данных в БД
def save_to_db_tg(post_time, text, post_link, source, photo_data=None):
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        query = """
            INSERT INTO telegram_posts (post_time, text, post_link, source, photo)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (post_time, text, post_link, source, pymysql.Binary(photo_data) if photo_data else None))
        conn.commit()
        return cursor.lastrowid
    except pymysql.MySQLError as e:
        print(f"Ошибка при сохранении данных: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
