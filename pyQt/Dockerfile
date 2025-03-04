# Используем официальный образ Python 3
FROM python

# Устанавливаем рабочую директорию
WORKDIR /usr/src/

# Копируем зависимости
COPY requirements.txt ./

# Устанавливаем зависимости (включая MySQL-коннектор)
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем системные зависимости для PyQt6
RUN apt-get update && apt-get install -y --no-install-recommends \
    qt6-base-dev python3-pyqt6 libx11-6 libxext-dev libxrender-dev \
    libxinerama-dev libxi-dev libxrandr-dev libxcursor-dev libxtst-dev \
    x11-xserver-utils xdg-utils libx11-6 libxext6 libxrender1 libxinerama1 \
    libxi6 libxrandr2 libxcursor1 libxtst6 libxkbcommon-x11-0 libdbus-1-3 \
    libfontconfig1 libfreetype6 libgl1-mesa-glx libegl1-mesa libsm6 libxcb1 \
    libxcb-cursor0 libxcb-keysyms1 libxcb-render0 libxcb-render-util0 libxcb-xinerama0 \
    libxcb-shape0 libxcb-shm0 libxcb-xfixes0 libxcb-sync1 libdbus-1-3 libxcb-cursor0 \
    libxcb-xinerama0 libxcb-randr0 libxcb-shape0 libxcb-shm0 libxcb-xfixes0 \
    libxcb-sync1 libxcb-render-util0 libxcb-render0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-util1 libx11-xcb1 libsm6 libxrender1 libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Копируем код проекта
COPY . .
#COPY . /usr/src/pyQt:/usr/src/data

# Добавляем переменные окружения
ENV DISPLAY=host.docker.internal:0.0
ENV PYTHONPATH=/usr/src/

# Запускаем PyQt приложение
CMD ["sh", "-c", "python ./pyQt/myQt.py"]
