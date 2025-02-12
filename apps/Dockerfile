#указываем с какого образа берем инфу
FROM python:3

WORKDIR /usr/src/apps

COPY requirements.txt ./
#выполняется один раз при первом запуске и все
RUN pip install --no-cache-dir -r requirements.txt
#точка значит что мы берем файлы из той же директории
COPY . .
#CMD запускается каждый раз с запуском проекта
CMD [ "python", "./main.py" ]
