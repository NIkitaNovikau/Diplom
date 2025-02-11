# database.py - Управление базой данных
import sqlite3

def create_db():
    """Создает таблицу для хранения новостей, если её нет."""
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            link TEXT UNIQUE,
            pub_date TEXT,
            description TEXT,
            image_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_news(source, title, link, pub_date, description, image_url):
    """Сохраняет новость в базу данных, если её там ещё нет."""
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO news (source, title, link, pub_date, description, image_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (source, title, link, pub_date, description, image_url))
    conn.commit()
    conn.close()

def get_all_news():
    """Извлекает все новости из базы данных."""
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    cursor.execute("SELECT source, title, link, pub_date, description, image_url FROM news")
    news = cursor.fetchall()
    conn.close()
    return news

if __name__ == "__main__":
    create_db()