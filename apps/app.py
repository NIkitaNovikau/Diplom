import requests
import xml.etree.ElementTree as ET
import re
import asyncio
from datetime import datetime
from data.database import create_db, save_news
from telethon import TelegramClient
from data.database_tg import create_database_tg, create_table_tg, post_exists_tg, save_to_db_tg

# Данные для подключения к Telegram
api_id = '25824542'
api_hash = '091a50633c4eaf345dc2079a79ec05b5'

# Источники (username → название)
sources = {
    "nevolf": "Невольфович",
    "pul_1": "Пул Первого"
}

# Словарь RSS-источников
rss_sources = {
    'Onliner': 'https://morss.it/:proxy/https://people.onliner.by/',
    'Спутник': 'https://morss.it/:proxy/https://sputnik.by/politics/'
}

# Создаём клиента Telethon
client = TelegramClient('session_name', api_id, api_hash)
"""Загружает RSS-ленту и возвращает её содержимое."""
def fetch_rss(url):
    try:
        response = requests.get(url, timeout=10)# Делаем GET-запрос к RSS-ленте, таймаут 10 сек.
        response.raise_for_status()  # Проверяем, нет ли ошибки (например, 404 или 500).
        return response.content # Возвращаем содержимое (XML-файл).
    except requests.RequestException as e:
        print(f"Ошибка загрузки {url}: {e}")
        return None

"""Разбирает XML и извлекает элементы <item>."""
def parse_items(xml_content):
    if xml_content:
        try:
            root = ET.fromstring(xml_content)  # Разбираем XML.
            '''fromstring(xml_content) – функция, которая:
            Принимает XML в виде строки (bytes или str).
            Преобразует его в объект Element, представляющий корневой элемент XML-дерева.
            Позволяет работать с XML как с объектной моделью.'''
            return root.findall('.//item')  # Находим все теги <item> (новости).
        except ET.ParseError as e:
            print(f"Ошибка парсинга XML: {e}")
    return []

# Функция очистки текста
def clean_text_tg(text):
    return re.sub(r'\[.*?\]\(.*?\)', '', text).strip()

"""Удаляет HTML-теги из текста."""
def clean_html(raw_html):
    """Использует регулярное выражение r'<.*?>',
     чтобы удалить все HTML-теги (<b>, <a>, <br> и т. д.).
     strip() убирает лишние пробелы по краям."""
    return re.sub(r'<.*?>', '', raw_html).strip()

"""Конвертирует дату из RSS-формата в MySQL-формат."""
def convert_date(pub_date):
    formats = [
        "%a, %d %b %Y %H:%M:%S GMT",  # "Mon, 05 Feb 2024 14:30:00 GMT"
        "%a %b %d %Y %H:%M:%S GMT%z (%Z)",  # "Sat Jun 29 2024 00:00:00 GMT+0000 (Coordinated Universal Time)"
        "%a %b %d %Y %H:%M:%S GMT%z",  # "Sat Jun 29 2024 00:00:00 GMT+0000"
        "%a, %d %b %Y %H:%M:%S %z"  # Новый формат → "Wed, 19 Feb 2025 10:30:44 +0300"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(pub_date, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    # Попробуем удалить текст в скобках и распарсить снова
    cleaned_date = re.sub(r"\s*\(.*?\)", "", pub_date).strip()
    for fmt in formats:
        try:
            return datetime.strptime(cleaned_date, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    print(f"Ошибка преобразования даты: {pub_date}")
    return None

"""Извлекает заголовок, ссылку, дату, описание и изображение из новости."""
def extract_news(item):
    '''item - это элемент XML, который содержит одну новость.
       .find('title') – это метод, который ищет элемент внутри item
       .strip() – это метод, который удаляет пробелы, переводы строк и лишние символы в начале и конце строки.'''
    title = item.find('title').text.strip() if item.find('title') is not None else 'Без заголовка'
    link = item.find('link').text.strip() if item.find('link') is not None else 'Без ссылки'
    pub_date = item.find('pubDate').text.strip() if item.find('pubDate') is not None else None
    pub_date = convert_date(pub_date) if pub_date else None  # Конвертация даты

    raw_description = item.find('description').text.strip() if item.find('description') is not None else 'Описание отсутствует'
    description = clean_html(raw_description)

    image_url = None
    for media_content in item.findall(".//{*}content"):
        ''' media_content.attrib['url'] → получает URL изображения
        media_content.attrib.get("medium") == "image" → проверяет, что контент — это изображение.
        Если "medium" нет, метод .get() вернет None (в отличие от media_content.attrib["medium"],
        который вызовет ошибку, если атрибута нет).'''
        if 'url' in media_content.attrib and media_content.attrib.get("medium") == "image":
            image_url = media_content.attrib['url']
            break

    return {
        'title': title,
        'link': link,
        'pub_date': pub_date,
        'description': description,
        'image_url': image_url
    }
"""Выводит новости в консоль и сохраняет их в базу данных."""
def print_news(news_list, source_name):
    print(f'\n=== Новости из {source_name} ===')
    for news in news_list:
        print(f'\nНазвание: {news["title"]}')
        print(f'   Ссылка: {news["link"]}')
        print(f'   Опубликовано: {news["pub_date"]}' if news["pub_date"] else '   Дата отсутствует')
        print(f'   Описание: {news["description"]}')
        print(f'   Изображение: {news["image_url"]}' if news["image_url"] else '   Изображение отсутствует')

        # Проверяем, есть ли дата перед сохранением
        if news["pub_date"]:
            save_news(source_name, news["title"], news["link"], news["pub_date"], news["description"], news["image_url"])
        else:
            print(f"Пропущена новость '{news['title']}', так как у неё некорректная дата.")

"""Проходит по всем RSS-источникам, загружает, парсит и обрабатывает новости."""
def fetch_all_rss():
    for source_name, rss_url in rss_sources.items():
        xml_content = fetch_rss(rss_url) # Вызывает fetch_rss(rss_url), чтобы загрузить XML-данные
        items = parse_items(xml_content) # Функция parse_items(xml_content) извлекает из XML все элементы <item>
        news_list = [extract_news(item) for item in items] # extract_news(item) — извлекает данные (заголовок, ссылку, дату, описание, изображение).
        print_news(news_list, source_name) # print_news выводит новости в консоль.

# Асинхронная функция для парсинга сообщений из нескольких каналов
async def fetch_all_messages():
    await client.start()

    for channel_username, source_name in sources.items():
        try:
            channel = await client.get_entity(f"t.me/{channel_username}")
        except Exception as e:
            print(f"Ошибка получения канала {channel_username}: {e}")
            continue

        messages = await client.get_messages(channel, limit=10)

        if not messages:
            print(f"Нет сообщений на канале {channel_username}.")
            continue

        for message in messages:
            post_time = message.date.strftime('%Y-%m-%d %H:%M:%S')
            cleaned_text = clean_text_tg(message.text or "")
            post_link = f"https://t.me/{channel_username}/{message.id}"  # Ссылка на пост
            photo_data = None

            # Проверяем, существует ли уже запись с таким временем
            if post_exists_tg(post_time, cleaned_text, post_link):
                print(f"Пропущено: ID {message.id} | {post_link}")
                continue

            if message.media and hasattr(message.media, 'photo'):
                photo_data = await client.download_media(message.media.photo, file=bytes)  # Получаем фото как байты

            record_id = save_to_db_tg(post_time, cleaned_text, post_link, source_name, photo_data)  # Получаем ID

            print(f"Сохранено: ID {record_id} | Источник: {source_name} | Время: {post_time} | Ссылка: {post_link} | Фото: {'Есть' if photo_data else 'Нет'}")

    await client.disconnect()

def main():
    create_db()
    create_database_tg()
    create_table_tg()
    fetch_all_rss()
    asyncio.run(fetch_all_messages())

