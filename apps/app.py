import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from database import create_db, save_news

# Словарь RSS-источников (название: ссылка)
rss_sources = {
    'БелТА': 'https://rss.app/feeds/XCdZXrlPIVc9IfT5.xml',
    'Спутник': 'https://rss.app/feeds/Q835OAfeWYwXWnpY.xml'
}

def fetch_rss(url):
    """ Загружает RSS-ленту и возвращает её содержимое."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Ошибка загрузки {url}: {e}")
        return None

def parse_items(xml_content):
    """Разбирает XML и извлекает элементы <item>."""
    if xml_content:
        try:
            root = ET.fromstring(xml_content)
            return root.findall('.//item')
        except ET.ParseError as e:
            print(f"Ошибка парсинга XML: {e}")
    return []

def clean_html(raw_html):
    """Удаляет HTML-теги из текста."""
    return re.sub(r'<.*?>', '', raw_html).strip()

def convert_date(pub_date):
    """Конвертирует дату из RSS-формата в MySQL-формат."""
    try:
        return datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S GMT").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"Ошибка преобразования даты: {pub_date}")
        return None  # Если не удалось преобразовать, возвращаем None

def extract_news(item):
    """Извлекает заголовок, ссылку, дату, описание и изображение из новости."""
    title = item.find('title').text.strip() if item.find('title') is not None else 'Без заголовка'
    link = item.find('link').text.strip() if item.find('link') is not None else 'Без ссылки'
    pub_date = item.find('pubDate').text.strip() if item.find('pubDate') is not None else None
    pub_date = convert_date(pub_date) if pub_date else None  # Конвертация даты

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
    """Выводит новости в консоль и сохраняет их в базу данных."""
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

def main():
    """Главная функция, запускающая парсинг всех RSS-лент и сохранение в БД."""
    create_db()
    for source_name, rss_url in rss_sources.items():
        xml_content = fetch_rss(rss_url)
        items = parse_items(xml_content)
        news_list = [extract_news(item) for item in items]
        print_news(news_list, source_name)

