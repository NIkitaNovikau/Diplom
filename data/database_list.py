import pymysql
from pymysql.err import MySQLError
from data.config_db import DB_CONFIG, db_config

# Функция для создания таблицы для RSS источников
def create_table_list_rss():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS rss_sources (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                source_name VARCHAR(255) NOT NULL,
                                rss_url VARCHAR(255) NOT NULL
                            )''')
        connection.commit()
    except MySQLError as e:
        print(f"Ошибка при создании таблицы для RSS: {e}")
    finally:
        connection.close()

# Функция для создания таблицы для Telegram источников
def create_table_list_tg():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS tg_sources (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                source_name VARCHAR(255) NOT NULL,
                                channel_username VARCHAR(255) NOT NULL
                            )''')
        connection.commit()
    except MySQLError as e:
        print(f"Ошибка при создании таблицы для Telegram: {e}")
    finally:
        connection.close()

# Функция для добавления RSS источников
def add_rss_source(source_name, rss_url):
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO rss_sources (source_name, rss_url) VALUES (%s, %s)", (source_name, rss_url))
        connection.commit()
    except MySQLError as e:
        print(f"Ошибка при добавлении RSS источника: {e}")
    finally:
        connection.close()

# Функция для добавления Telegram источников
def add_tg_source(source_name, channel_username):
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO tg_sources (source_name, channel_username) VALUES (%s, %s)", (source_name, channel_username))
        connection.commit()
    except MySQLError as e:
        print(f"Ошибка при добавлении Telegram источника: {e}")
    finally:
        connection.close()

# Функция для удаления RSS источников по ID с сбросом AUTO_INCREMENT
def remove_rss_source(source_name):
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM rss_sources WHERE source_name = %s", (source_name,))
            cursor.execute("ALTER TABLE rss_sources AUTO_INCREMENT = 1")  # Сбрасываем AUTO_INCREMENT
        connection.commit()
    except MySQLError as e:
        print(f"Ошибка при удалении RSS источника: {e}")
    finally:
        connection.close()

# Функция для удаления Telegram источников по ID с сбросом AUTO_INCREMENT
def remove_tg_source(source_name):
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tg_sources WHERE source_name = %s", (source_name,))
            cursor.execute("ALTER TABLE tg_sources AUTO_INCREMENT = 1")  # Сбрасываем AUTO_INCREMENT
        connection.commit()
    except MySQLError as e:
        print(f"Ошибка при удалении Telegram источника: {e}")
    finally:
        connection.close()

# Функция для получения всех RSS источников
def get_rss_sources():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("SELECT source_name, rss_url FROM rss_sources")
            return cursor.fetchall()
    except MySQLError as e:
        print(f"Ошибка при получении RSS источников: {e}")
        return []
    finally:
        connection.close()

# Функция для получения всех Telegram источников
def get_tg_sources():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT source_name, channel_username FROM tg_sources")
            return cursor.fetchall()
    except MySQLError as e:
        print(f"Ошибка при получении Telegram источников: {e}")
        return []
    finally:
        connection.close()
