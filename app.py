import requests
import xml.etree.ElementTree as ET
import re
from database import create_db, save_news

# Словарь RSS-источников (название: ссылка)
rss_sources = {
    'БелТА': 'https://rss.app/feeds/XCdZXrlPIVc9IfT5.xml',
    'Спутник': 'https://rss.app/feeds/Q835OAfeWYwXWnpY.xml'
}

def fetch_rss(url):
    """ Загружает RSS-ленту и возвращает её содержимое."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Ошибка загрузки {url}: {response.status_code}")
        return None

def parse_items(xml_content):
    """Разбирает XML и извлекает элементы <item>."""
    if xml_content:
        root = ET.fromstring(xml_content)
        return root.findall('.//item')
    return []

def clean_html(raw_html):
    """Удаляет HTML-теги из текста."""
    return re.sub(r'<.*?>', '', raw_html).strip()

def extract_news(item):
    """Извлекает заголовок, ссылку, дату, описание и изображение из новости."""
    title = item.find('title').text.strip() if item.find('title') is not None else 'Без заголовка'
    link = item.find('link').text.strip() if item.find('link') is not None else 'Без ссылки'
    pub_date = item.find('pubDate').text.strip() if item.find('pubDate') is not None else 'Неизвестная дата'
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
        print(f'   Опубликовано: {news["pub_date"]}')
        print(f'   Описание: {news["description"]}')
        print(f'   Изображение: {news["image_url"]}' if news["image_url"] else '   Изображение отсутствует')
        save_news(source_name, news["title"], news["link"], news["pub_date"], news["description"], news["image_url"])

def main():
    """Главная функция, запускающая парсинг всех RSS-лент и сохранение в БД."""
    create_db()
    for source_name, rss_url in rss_sources.items():
        xml_content = fetch_rss(rss_url)
        items = parse_items(xml_content)
        news_list = [extract_news(item) for item in items]
        print_news(news_list, source_name)