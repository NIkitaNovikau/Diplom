import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from data.database import get_all_news_rss

class NewsApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Новости из MySQL")
        self.setGeometry(100, 100, 800, 500)

        layout = QVBoxLayout()

        self.loadButton = QPushButton("Загрузить новости")
        self.loadButton.clicked.connect(self.load_data)
        layout.addWidget(self.loadButton)

        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        self.setLayout(layout)

    def load_data(self):
        """Загружает данные из MySQL в таблицу"""
        print("[DEBUG] Подключение к MySQL...")
        data = get_all_news_rss()
        if not data:
            print("[DEBUG] Данных нет, таблица остается пустой")
            return

        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Источник", "Заголовок", "Ссылка", "Дата"])

        for row, news in enumerate(data):
            for col, value in enumerate(news):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(row, col, item)

        print(f"[DEBUG] Загружено {len(data)} записей")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewsApp()
    window.show()
    sys.exit(app.exec())
