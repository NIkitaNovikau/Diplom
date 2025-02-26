import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, \
    QTableWidgetItem, QTextEdit
from PyQt6.QtCore import Qt, QTimer

from data.database import get_all_news_rss
from data.database_tg import get_all_news_tg


class NewsApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Новости из MySQL")
        self.setGeometry(100, 100, 1000, 700)  # Увеличили размер окна
        self.setMinimumSize(800, 600)  # Устанавливаем минимальный размер окна для растягивания

        layout = QVBoxLayout()

        # Layout for buttons
        button_layout = QHBoxLayout()

        self.loadRssButton = QPushButton("Прочесть новости с RSS ленты")
        self.loadRssButton.clicked.connect(self.load_rss_data)
        button_layout.addWidget(self.loadRssButton)

        self.loadTgButton = QPushButton("Прочесть новости с TG каналов")
        self.loadTgButton.clicked.connect(self.load_tg_data)
        button_layout.addWidget(self.loadTgButton)

        self.loadAllButton = QPushButton("Загрузить все новости")
        self.loadAllButton.clicked.connect(self.load_all_data)
        button_layout.addWidget(self.loadAllButton)

        layout.addLayout(button_layout)

        # Table for displaying news
        self.newsTable = QTableWidget()
        self.newsTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Выбор всей строки
        self.newsTable.setSortingEnabled(True)  # Включаем сортировку по всем столбцам
        layout.addWidget(self.newsTable)

        # Text area for detailed news information
        self.detailText = QTextEdit()
        self.detailText.setReadOnly(True)
        layout.addWidget(self.detailText)

        self.setLayout(layout)

        # Добавляем обработчик выбора строки
        self.newsTable.itemSelectionChanged.connect(self.show_news_detail)

    def load_rss_data(self):
        """Загружает новости из MySQL RSS в таблицу"""
        print("[DEBUG] Подключение к MySQL для RSS...")
        data = get_all_news_rss()
        self.update_table(data, "RSS")

    def load_tg_data(self):
        """Загружает новости из MySQL TG в таблицу"""
        print("[DEBUG] Подключение к MySQL для TG...")
        data = get_all_news_tg()
        self.update_table(data, "TG")

    def load_all_data(self):
        """Загружает все новости из MySQL"""
        print("[DEBUG] Подключение к MySQL для всех новостей...")
        rss_data = get_all_news_rss()
        tg_data = get_all_news_tg()
        combined_data = rss_data + tg_data  # Объединяем данные из RSS и TG
        self.update_table(combined_data, "Все новости")

    def update_table(self, data, source):
        """Обновляет таблицу с новостями"""
        if not data:
            print(f"[DEBUG] Данных нет для {source}, таблица остается пустой")
            return

        # Устанавливаем количество строк в зависимости от данных
        self.newsTable.setRowCount(len(data))

        # Устанавливаем количество столбцов и их заголовки
        self.newsTable.setColumnCount(4)
        self.newsTable.setHorizontalHeaderLabels(["Источник", "Заголовок", "Ссылка", "Дата"])

        # Устанавливаем ширину столбцов для удобства
        self.newsTable.setColumnWidth(0, 150)  # Источник
        self.newsTable.setColumnWidth(1, 350)  # Заголовок
        self.newsTable.setColumnWidth(2, 300)  # Ссылка
        self.newsTable.setColumnWidth(3, 150)  # Дата

        # Используем QTimer для того, чтобы добавить строки с небольшими задержками
        for row, news in enumerate(data):
            QTimer.singleShot(row * 10, lambda r=row, n=news: self.add_row(r, n))

        print(f"[DEBUG] Загружено {len(data)} записей из {source}")

    def add_row(self, row, news):
        """Добавляет строку с новостью в таблицу"""
        for col, value in enumerate(news):
            item = QTableWidgetItem(str(value))
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.newsTable.setItem(row, col, item)

    def show_news_detail(self):
        """Отображает подробную информацию о выбранной новости"""
        selected_rows = set(index.row() for index in self.newsTable.selectedIndexes())  # Получаем выбранные строки
        if not selected_rows:
            return  # Если ничего не выбрано, выходим из метода

        # Берем первую выбранную строку (если выбрано несколько)
        row = next(iter(selected_rows))

        # Получаем данные из строки
        source = self.newsTable.item(row, 0).text()
        title = self.newsTable.item(row, 1).text()
        link = self.newsTable.item(row, 2).text()
        date = self.newsTable.item(row, 3).text()

        # Формируем текст для отображения
        detail_text = f"Источник: {source}\nЗаголовок: {title}\nСсылка: {link}\nДата: {date}"
        self.detailText.setText(detail_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewsApp()
    window.show()
    sys.exit(app.exec())
