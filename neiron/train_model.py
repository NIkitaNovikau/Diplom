import torch
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from datetime import datetime
import os
import json
import matplotlib.pyplot as plt
import accelerate

# Функция загрузки данных из БД
def fetch_news_from_db():
    engine = create_engine("mysql+pymysql://root:1111@localhost:3306/newsNeiron")
    query = "SELECT title, importance FROM news"
    # тута создаем табличку с колонками title, importance
    df = pd.read_sql(query, engine)
    # Проверяем баланс классов
    # df['importance'] – выбираем колонку importance.
    # .value_counts() – считает, сколько раз встречается 0 и 1.
    class_counts = df['importance'].value_counts()
    # class_counts.to_dict() – превращает value_counts() в словарь
    print(f"Баланс классов: {class_counts.to_dict()}")
    return df


# Загружаем токенизатор
# Разбивает текст на токены и превращает в числа
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')


# Функция токенизации текста
'''examples — это словарь, где examples['text'] — список текстов.
padding - это ограничение по размеру(20) слов
truncation - отсекает лишние'''
def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', max_length=20, truncation=True)


# Подготовка данных для обучения
def prepare_data():
    df = fetch_news_from_db()
    # Разделяем на 80% (обучение) и 20% (тест)
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        df['title'], df['importance'], test_size=0.2, random_state=12
    )
    # Создаем Dataset
    '''Dataset({
    'text': ["Президент подписал указ", "Курс доллара вырос на 2%", ...],
    'labels': [1, 1, 0, 1, ...]
    })'''
    train_data = Dataset.from_dict({'text': train_texts.tolist(), 'labels': train_labels.tolist()})
    test_data = Dataset.from_dict({'text': test_texts.tolist(), 'labels': test_labels.tolist()})
    # Токенизируем данные
    # Применяет tokenize_function() ко всем заголовкам сразу.
    # batched=True – ускоряет обработку пакетами.
    train_data = train_data.map(tokenize_function, batched=True)
    test_data = test_data.map(tokenize_function, batched=True)
    return train_data, test_data

# Функция поиска trainer_state.json в чекпойнтах
def find_trainer_state():
    results_dir = "./results"
    if os.path.exists(results_dir):
        for checkpoint in sorted(os.listdir(results_dir),
                                 key=lambda x: int(x.split('-')[-1]) if x.startswith("checkpoint-") and x.split('-')[
                                     -1].isdigit() else -1, reverse=True):
            trainer_state_path = os.path.join(results_dir, checkpoint, "trainer_state.json")
            if os.path.exists(trainer_state_path):
                print(f"✅ Используем trainer_state.json из {checkpoint}")
                return trainer_state_path
    print("⚠️ Файл trainer_state.json не найден в чекпойнтах.")
    return None

# Функция построения графиков
def plot_training_metrics():
    trainer_state_path = find_trainer_state()
    if trainer_state_path:
        with open(trainer_state_path, "r") as file:
            trainer_state = json.load(file)

        log_history = trainer_state.get("log_history", [])

        train_loss = [log["loss"] for log in log_history if "loss" in log]
        eval_loss = [log["eval_loss"] for log in log_history if "eval_loss" in log]
        epochs_train = range(1, len(train_loss) + 1)
        epochs_eval = range(1, len(eval_loss) + 1)

        # Проверяем, есть ли метрики точности
        eval_accuracy = [log["eval_accuracy"] for log in log_history if "eval_accuracy" in log]
        eval_f1 = [log["eval_f1"] for log in log_history if "eval_f1" in log]

        plt.figure(figsize=(12, 5))

        # График потерь
        plt.subplot(1, 2, 1)
        plt.plot(epochs_train, train_loss, 'bo-', label='Training loss')
        if eval_loss:
            plt.plot(epochs_eval, eval_loss, 'ro-', label='Validation loss')
        plt.title('Training & Validation Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()

        # График метрик точности (если есть)
        if eval_accuracy or eval_f1:
            plt.subplot(1, 2, 2)
            if eval_accuracy:
                plt.plot(range(1, len(eval_accuracy) + 1), eval_accuracy, 'go-', label='Validation Accuracy')
            if eval_f1:
                plt.plot(range(1, len(eval_f1) + 1), eval_f1, 'mo-', label='Validation F1-score')
            plt.title('Validation Metrics')
            plt.xlabel('Epochs')
            plt.ylabel('Score')
            plt.legend()

        plt.tight_layout()
        plt.show()
    else:
        print("Файл trainer_state.json не найден.")

# Функция расчета метрик
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    accuracy = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}

# Функция для оценки точности модели
def evaluate_model(model, test_data, trainer):
    print("Оценка модели на тестовых данных...")
    # хранит логиты(которые потом преобразуем в окончательные метки класса)
    predictions = trainer.predict(test_data)
    # извлекаем логиты
    logits = predictions.predictions
    # Преобразуем логиты в метки классов.
    # Функция torch.argmax находит индекс максимального логита, который и будет соответствовать предсказанному классу
    preds = torch.argmax(torch.tensor(logits), dim=-1)  # Переводим логиты в 0/1
    # а это истиные значения
    labels = torch.tensor(test_data['labels'])

    accuracy = (preds.numpy() == labels.numpy()).mean()
    print(f"Точность модели: {accuracy * 100:.2f}%")

    # Выводим 5 примеров предсказаний
    for i in range(5):
        print(f"\n🔎 Тестовая новость {i + 1}:")
        print(f"Текст: {test_data['text'][i][:100]}...")  # Ограничиваем длину вывода
        print(f"Предсказание: {preds[i].item()} (0 - неважная, 1 - важная)")
        print(f"Истинное значение: {labels[i].item()}")
# Функция обучения модели
def train_model():
    train_data, test_data = prepare_data()
    model_path = "./bert_news_model"

    try:
        model = BertForSequenceClassification.from_pretrained(model_path)
        print("✅ Загружена старая модель для дообучения!")
    except:
        model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
        print("⚠️ Старая модель не найдена, начинаем обучение с нуля.")

    '''output_dir='./results' — указывает, куда будут сохраняться результаты обучения (например, веса модели).
          num_train_epochs=3 — количество эпох для обучения модели. Модель будет проходить по всем данным 3 раза.
          per_device_train_batch_size=8 — размер батча (пакета данных) для тренировки, т.е. количество примеров, которые обрабатываются за один шаг.
          per_device_eval_batch_size=8 — размер батча для оценки модели на тестовых данных.
          warmup_steps=500 — количество шагов (итераций), когда будет происходить "разогрев" (увеличение скорости обучения от 0 до начального значения).
          weight_decay=0.01 — коэффициент веса для регуляризации (предотвращает переобучение модели).
          logging_dir='./logs' — директория, в которой будут сохраняться лог-файлы.
          logging_steps=10 — каждые 10 шагов обучения будет выводиться лог.'''

    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=20,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_steps=100,
        weight_decay=0.1,
        learning_rate=2e-5,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy='no',
        save_strategy='epoch',
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_data,
        eval_dataset=test_data,
        compute_metrics=compute_metrics
    )

    print("Начинаем дообучение модели...")
    trainer.train()
    print("✅ Обучение завершено!")

    # Сохраняем новую версию модели с датой
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    new_model_path = f"./bert_news_model_{timestamp}"
    model.save_pretrained(new_model_path)
    tokenizer.save_pretrained(new_model_path)
    print(f"✅ Новая версия модели сохранена в: {new_model_path}")

    # Оцениваем модель после обучения
    #evaluate_model(model, test_data, trainer)


def predict_importance():
    model_path = "./bert_news_model_20250312_0729"
    model = BertForSequenceClassification.from_pretrained(model_path)
    model.eval()
    while True:
        title = input("Введите заголовок новости (или 'exit' для выхода): ")
        if title.lower() == 'exit':
            break
        inputs = tokenizer(title, return_tensors="pt", padding=True, truncation=True, max_length=20)
        with torch.no_grad():
            logits = model(**inputs).logits
        pred = torch.argmax(logits, dim=-1).item()
        print("❗ Важная новость" if pred == 1 else "ℹ️ Неважная новость")


if __name__ == "__main__":
     train_model()
    # Построение графиков
    #plot_training_metrics()
    # Определение важности новости
    #predict_importance()
