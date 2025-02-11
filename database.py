import sqlite3
#нужно чтобы не удаляла а чтобы не записывало такое же
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
    # Добавим уникальность по ссылке, чтобы избежать дублирования
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_news_link ON news (link)
    ''')
    conn.commit()
    conn.close()


def save_news(source, title, link, pub_date, description, image_url):
    """Сохраняет новость в базу данных, если её там ещё нет."""
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()

    # Проверяем, существует ли новость с таким же link
    cursor.execute("SELECT 1 FROM news WHERE link = ?", (link,))
    existing_news = cursor.fetchone()

    if not existing_news:
        try:
            cursor.execute(''' 
                INSERT INTO news (source, title, link, pub_date, description, image_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (source, title, link, pub_date, description, image_url))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при вставке новости: {e}")
    else:
        print("Новость с такой ссылкой уже существует.")

    conn.close()


def remove_duplicates():
    """Удаляет дубликаты из базы данных, оставляя только последние по времени записи."""
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM news
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM news
            GROUP BY link
        )
    ''')
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

