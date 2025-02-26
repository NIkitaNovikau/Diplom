import requests
import xml.etree.ElementTree as ET
import re
import asyncio
from datetime import datetime
from data.database import create_database_rss, create_table_rss, save_news_rss, get_all_news_rss
from telethon import TelegramClient
from data.database_tg import create_database_tg, create_table_tg, post_exists_tg, save_to_db_tg
from data.database_list import get_rss_sources, get_tg_sources, create_table_list_rss, create_table_list_tg, add_tg_source, add_rss_source, remove_rss_source, remove_tg_source

# Данные для подключения к Telegram
api_id = '25824542'
api_hash = '091a50633c4eaf345dc2079a79ec05b5'

# Создаём клиента Telethon
client = TelegramClient('session_name', api_id, api_hash)

def fetch_rss(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Ошибка загрузки {url}: {e}")
        return None

def parse_items(xml_content):
    if xml_content:
        try:
            root = ET.fromstring(xml_content)
            return root.findall('.//item')
        except ET.ParseError as e:
            print(f"Ошибка парсинга XML: {e}")
    return []

def clean_text_tg(text):
    return re.sub(r'\[.*?\]\(.*?\)', '', text).strip()

def clean_html(raw_html):
    return re.sub(r'<.*?>', '', raw_html).strip()

def convert_date(pub_date):
    formats = [
        "%a, %d %b %Y %H:%M:%S GMT",
        "%a %b %d %Y %H:%M:%S GMT%z (%Z)",
        "%a %b %d %Y %H:%M:%S GMT%z",
        "%a, %d %b %Y %H:%M:%S %z"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(pub_date, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    cleaned_date = re.sub(r"\s*\(.*?\)", "", pub_date).strip()
    for fmt in formats:
        try:
            return datetime.strptime(cleaned_date, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    print(f"Ошибка преобразования даты: {pub_date}")
    return None

def extract_news(item):
    title = item.find('title').text.strip() if item.find('title') is not None else 'Без заголовка'
    link = item.find('link').text.strip() if item.find('link') is not None else 'Без ссылки'
    pub_date = item.find('pubDate').text.strip() if item.find('pubDate') is not None else None
    pub_date = convert_date(pub_date) if pub_date else None

    raw_description = item.find('description').text.strip() if item.find('description') is not None else 'Описание отсутствует'
    description = clean_html(raw_description)

    image_url = None
    for media_content in item.findall(".//{*}content"):
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

def print_news(news_list, source_name):
    print(f'\n=== Новости из {source_name} ===')
    for news in news_list:
        print(f'\nНазвание: {news["title"]}')
        print(f'   Ссылка: {news["link"]}')
        print(f'   Опубликовано: {news["pub_date"]}' if news["pub_date"] else '   Дата отсутствует')
        print(f'   Описание: {news["description"]}')
        print(f'   Изображение: {news["image_url"]}' if news["image_url"] else '   Изображение отсутствует')

        if news["pub_date"]:
            save_news_rss(source_name, news["title"], news["link"], news["pub_date"], news["description"], news["image_url"])
        else:
            print(f"Пропущена новость '{news['title']}', так как у неё некорректная дата.")

def fetch_all_rss():
    rss_sources = get_rss_sources()  # Получаем источники из базы данных
    for source_name, rss_url in rss_sources:
        xml_content = fetch_rss(rss_url)
        items = parse_items(xml_content)
        news_list = [extract_news(item) for item in items]
        print_news(news_list, source_name)

async def fetch_all_tg():
    await client.start()

    tg_sources = get_tg_sources()  # Получаем Telegram источники из базы данных
    for channel_username, source_name in tg_sources:
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
            post_link = f"https://t.me/{channel_username}/{message.id}"

            if post_exists_tg(post_time, cleaned_text, post_link):
                print(f"Пропущено: ID {message.id} | {post_link}")
                continue

            photo_data = None
            if message.media and hasattr(message.media, 'photo'):
                photo_data = await client.download_media(message.media.photo, file=bytes)

            record_id = save_to_db_tg(post_time, cleaned_text, post_link, source_name, photo_data)
            print(f"Сохранено: ID {record_id} | Источник: {source_name} | Время: {post_time} | Ссылка: {post_link} | Фото: {'Есть' if photo_data else 'Нет'}")

    await client.disconnect()


def add_rss_source_input():
    source_name = input("Введите название RSS источника: ")
    rss_url = input("Введите URL RSS источника: ")
    add_rss_source(source_name, rss_url)
    print(f"Источник '{source_name}' добавлен в базу данных.")


def add_tg_source_input():
    channel_username = input("Введите название канала Telegram: ")
    source_name = input("Введите username источника: ")
    add_tg_source(channel_username, source_name)
    print(f"Telegram источник '{source_name}' добавлен в базу данных.")


def delete_rss_source_input():
    source_name = input("Введите название RSS источника для удаления: ")
    remove_rss_source(source_name)
    print(f"Источник '{source_name}' удалён из базы данных.")


def delete_tg_source_input():
    source_name = input("Введите название Telegram источника для удаления: ")
    remove_tg_source(source_name)
    print(f"Telegram источник '{source_name}' удалён из базы данных.")

def add_sources():
    while True:
        print("\nВыберите действие:")
        print("1. Добавить RSS источник")
        print("2. Добавить Telegram источник")
        print("3. Удалить RSS источник")
        print("4. Удалить Telegram источник")
        print("5. Завершить")

        choice = input("Ваш выбор: ")

        if choice == "1":
            add_rss_source_input()
        elif choice == "2":
            add_tg_source_input()
        elif choice == "3":
            delete_rss_source_input()
        elif choice == "4":
            delete_tg_source_input()
        elif choice == "5":
            break
        else:
            print("Некорректный выбор. Попробуйте снова.")
def main():
    create_database_rss()
    create_table_rss()
    create_database_tg()
    create_table_tg()
    create_table_list_rss()
    create_table_list_tg()
    add_sources()
    fetch_all_rss()
    asyncio.run(fetch_all_tg())
