# Используем официальный образ Python 3
FROM python

# Устанавливаем рабочую директорию
WORKDIR /usr/src/apps

# Копируем зависимости
COPY requirements.txt ./

# Устанавливаем зависимости (включая MySQL-коннектор)
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# Добавляем ожидание MySQL перед запуском
CMD ["sh", "-c", "sleep 10 && python ./main.py"]
