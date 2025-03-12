import pymysql
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import pandas as pd
from sqlalchemy import create_engine
import numpy as np


# Загрузка модели и токенизатора
print("🔄 Загрузка модели и токенизатора...")
model = BertForSequenceClassification.from_pretrained('./bert_news_model_20250312_0729')
tokenizer = BertTokenizer.from_pretrained('./bert_news_model_20250312_0729')
print("✅ Модель загружена!")


# Подключение к БД и выборка новостей
def fetch_news_from_db():
    print("🔄 Подключение к базе данных...")
    engine = create_engine("mysql+pymysql://root:1111@localhost:3306/news")

    query = "SELECT id, title FROM news WHERE importance IS FALSE"
    df = pd.read_sql(query, con=engine)

    print(f"📥 Загружено {len(df)} новостей для обработки.")
    return df


# Функция предсказания важности новости
def predict_importance(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    outputs = model(**inputs)

    logits = outputs.logits.detach().numpy()
    prediction = np.argmax(logits)

    print(f"🔮 Предсказание: {prediction} (0 - неважная, 1 - важная)")
    print(f"Логиты: {logits}\n")

    return prediction


# Обновление новостей в БД
def update_news_in_db():
    news_df = fetch_news_from_db()

    if news_df.empty:
        print("❌ Нет новостей для обработки.")
        return

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='1111',
        database='news',
        port=3306
    )

    print("🔄 Обновление новостей в базе данных...")

    for _, row in news_df.iterrows():
        title = row['title']
        importance = predict_importance(title)

        query = "UPDATE news SET importance = %s WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (importance, row['id']))
        connection.commit()

    print("✅ Обновление завершено!")
    connection.close()


if __name__ == "__main__":
    update_news_in_db()
