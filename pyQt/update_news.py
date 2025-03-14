import pymysql
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np
from data.config_db import DB_CONFIG

# Загрузка модели и токенизатора
print("🔄 Загрузка модели и токенизатора...")
try:
    model_path = "./bert_news_model_20250312_0729"
    model = BertForSequenceClassification.from_pretrained(model_path)
    tokenizer = BertTokenizer.from_pretrained(model_path)
    print("✅ Модель загружена!")
except Exception as e:
    print(f"❌ Ошибка при загрузке модели: {e}")
    exit()

# Выборка новостей без важности
def fetch_news_from_db():
    try:
        print("🔄 Подключение к базе данных...")
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title FROM news WHERE importance IS FALSE")
            news = cursor.fetchall()
        connection.close()
        print(f"Загружено {len(news)} новостей для обработки.")
        return news
    except pymysql.MySQLError as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        return []
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        return []

# Функция предсказания важности новости
def predict_importance(text):
    try:
        inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
        outputs = model(**inputs)
        logits = outputs.logits.detach().numpy()
        prediction = int(np.argmax(logits))
        print(f"Предсказание: {prediction} (0 - неважная, 1 - важная)")
        print(f"Логиты: {logits}\n")
        return prediction
    except Exception as e:
        print(f"❌ Ошибка при предсказании важности: {e}")
        return 0

# Обновление новостей в БД
def update_news_in_db():
    try:
        news_list = fetch_news_from_db()
        if not news_list:
            print("Нет новостей для обработки.")
            return

        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            for news in news_list:
                importance = predict_importance(news['title'])
                cursor.execute("UPDATE news SET importance = %s WHERE id = %s", (importance, news['id']))
            connection.commit()
        connection.close()
        print("✅ Обновление завершено!")
    except pymysql.MySQLError as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")

# Получение важных новостей из БД
def get_important_news_from_db():
    try:
        print("🔄 Получение важных новостей...")
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, source, title, link, pub_date, viewed, who FROM news WHERE importance = TRUE")
            important_news = cursor.fetchall()
        connection.close()
        print(f"Найдено {len(important_news)} важных новостей.")
        return important_news
    except pymysql.MySQLError as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        return []
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        return []

if __name__ == "__main__":
    get_important_news_from_db()
