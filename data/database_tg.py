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
                post_link VARCHAR(255),
                viewed BOOL,
                who TEXT
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
            INSERT INTO telegram_posts (post_time, text, post_link, source, photo, viewed, who)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (post_time, text, post_link, source, pymysql.Binary(photo_data) if photo_data else None, 0, "TG"))
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
def get_all_news_tg():
    """Получает данные из MySQL"""
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, source, text, post_link, post_time, viewed, who FROM telegram_posts ORDER BY post_time DESC")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except pymysql.MySQLError as e:
        print("Ошибка при работе с базой данных:", e)
        return []

# Функция для пометки новости как прочитанной в базе данных для TG
def mark_news_as_viewed_tg(news_id):
    try:
        # Подключение к базе данных
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        # Обновляем запись в таблице TG новостей, где название новости соответствует "title"
        query = "UPDATE telegram_posts SET viewed = 1 WHERE id = %s"
        cursor.execute(query, (news_id,))

        # Сохраняем изменения
        connection.commit()
        print(f"Новость '{news_id}' успешно помечена как прочитанная в TG.")
    except pymysql.MySQLError as e:
        print(f"Ошибка при пометке новости '{news_id}' как прочитанной: {e}")
    finally:
        # Закрываем соединение
        connection.close()
def add_columns_to_telegram_posts():
    try:
        # Подключение к базе данных
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='1111',
            database='news',
            port=3306
        )
        cursor = connection.cursor()

        # Проверяем, существует ли столбец "who"
        cursor.execute("SHOW COLUMNS FROM news LIKE 'who'")
        result_who = cursor.fetchone()

        if not result_who:
            # Добавляем новый столбец "who" без DEFAULT
            cursor.execute("ALTER TABLE news ADD COLUMN who TEXT")
            cursor.execute("UPDATE news SET who = 'RSS'")
            connection.commit()  # Сохраняем изменения
            print("Столбец 'who' успешно добавлен и заполнен значением 'RSS' в таблице telegram_posts.")
        else:
            print("Столбец 'who' уже существует в таблице telegram_posts.")

    except pymysql.MySQLError as e:
        print(f"Ошибка при добавлении столбцов: {e}")
    finally:
        connection.close()


