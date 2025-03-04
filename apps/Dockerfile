# Используем официальный образ Python 3
FROM python

# Устанавливаем рабочую директорию
WORKDIR /usr/src/

# Копируем зависимости
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY . .
#COPY . /usr/src/apps:/usr/src/data

# Устанавливаем переменную окружения
ENV PYTHONPATH=/usr/src/

# Запускаем парсер
CMD ["sh", "-c", "sleep 10 && python ./apps/main.py"]
