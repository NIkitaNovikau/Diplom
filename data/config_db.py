# Данные для подключения к MySQL_tg
db_config = {
    "host": "localhost",  # Для докера: "host.docker.internal"
    "user": "root",
    "password": "1111",
    "database": "tgnews",  # Имя базы данных
    "port": 3306
}
# Конфигурация подключения к MySQL_rss
DB_CONFIG = {
    "host": "localhost",  #для докера нужен host.docker.internal
    "user": "root",
    "password": "1111",
    "database": "news",  # Имя базы данных
    "port": 3306
}


def update_table(self, data, source):
    self.page1.newsTable.setRowCount(len(data))
    self.page1.newsTable.setColumnCount(5)  # Теперь 5 столбцов, включая ID
    self.page1.newsTable.setHorizontalHeaderLabels(["ID", "Источник", "Заголовок", "Ссылка", "Дата"])

    for row, news in enumerate(data):
        self.add_row(row, news)

    self.page1.newsTable.setColumnHidden(0, True)  # Скрываем столбец ID


def add_row(self, row, news):
    if len(news) < 5:
        print(f"[ERROR] Некорректные данные в строке {row}: {news}")
        return  # Если данных меньше 5, пропускаем строку

    news_id, source, title, link, pub_date = news  # Распаковываем кортеж

    self.page1.newsTable.setItem(row, 0, QTableWidgetItem(str(news_id)))  # ID (скрытый)
    self.page1.newsTable.setItem(row, 1, QTableWidgetItem(source))
    self.page1.newsTable.setItem(row, 2, QTableWidgetItem(title))
    self.page1.newsTable.setItem(row, 3, QTableWidgetItem(link))
    self.page1.newsTable.setItem(row, 4, QTableWidgetItem(str(pub_date)))  # Дата в строковом формате

    # Делаем ячейки только для чтения
    for col in range(5):
        item = self.page1.newsTable.item(row, col)
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

def show_news_detail(self):
    selected_rows = set(index.row() for index in self.newsTable.selectedIndexes())
    if not selected_rows:
        return

    row = next(iter(selected_rows))

    # Получаем ID из скрытого столбца
    news_id = self.newsTable.item(row, 0).text()
    source = self.newsTable.item(row, 1).text()
    title = self.newsTable.item(row, 2).text()
    link = self.newsTable.item(row, 3).text()
    date = self.newsTable.item(row, 4).text()

    detail_text = f"Источник: {source}\nЗаголовок: {title}\nСсылка: {link}\nДата: {date}"
    self.detailText.setText(detail_text)

    # Помечаем новость как прочитанную
    self.mark_as_read(news_id, row)

def mark_as_read(self, news_id, row):
    # Обновляем запись в базе
    mark_news_as_viewed_rss(news_id)  # или mark_news_as_viewed_tg в зависимости от источника

    # Обновляем строку в таблице
    QTimer.singleShot(500, lambda: self.update_row_to_gray(row))