import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, \
    QTableWidgetItem, QTextEdit, QStackedWidget, QSizePolicy
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QBrush, QPalette
from data.database import get_all_news_rss
from data.database_tg import get_all_news_tg


class Page1(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent  # Сохраняем ссылку на родительский объект
        self.setUpUI()

    def setUpUI(self):
        layout = QVBoxLayout()

        # Статичный layout с кнопками для переключения страниц
        button_layout_db = QHBoxLayout()

        self.loadRssButton = QPushButton("Прочесть новости с RSS\nленты")
        self.loadRssButton.clicked.connect(self.load_rss_data)
        self.loadRssButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout_db.addWidget(self.loadRssButton)

        self.loadTgButton = QPushButton("Прочесть новости с TG\nканалов")
        self.loadTgButton.clicked.connect(self.load_tg_data)
        self.loadTgButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout_db.addWidget(self.loadTgButton)

        self.loadAllButton = QPushButton("Загрузить все\nновости")
        self.loadAllButton.clicked.connect(self.load_all_data)
        self.loadAllButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout_db.addWidget(self.loadAllButton)

        # Добавляем кнопки работы с БД в основное содержимое
        layout.addLayout(button_layout_db)

        # Создаем таблицу для новостей
        self.newsTable = QTableWidget()
        self.newsTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Выделение целых строк
        self.newsTable.setSortingEnabled(True)  # Включаем сортировку по столбцам
        layout.addWidget(self.newsTable)

        # Создаем текстовое поле для деталей новости
        self.detailText = QTextEdit()
        layout.addWidget(self.detailText)

        self.setLayout(layout)

        # Подключаем обработчик события выбора строки в таблице
        self.newsTable.itemSelectionChanged.connect(self.show_news_detail)

    def load_rss_data(self):
        print("[DEBUG] Подключение к MySQL для RSS...")
        # Получаем новости из RSS
        data = get_all_news_rss()
        # Обновляем таблицу данными из RSS
        self.parent.update_table(data, "RSS")

    def load_tg_data(self):
        print("[DEBUG] Подключение к MySQL для TG...")
        # Получаем новости из TG
        data = get_all_news_tg()
        # Обновляем таблицу данными из TG
        self.parent.update_table(data, "TG")

    def load_all_data(self):
        print("[DEBUG] Подключение к MySQL для всех новостей...")
        # Получаем данные из RSS и TG
        rss_data = get_all_news_rss()
        tg_data = get_all_news_tg()
        # Объединяем данные из обоих источников
        combined_data = rss_data + tg_data
        # Обновляем таблицу с комбинированными данными
        self.parent.update_table(combined_data, "Все новости")

    # Отображает подробную информацию о выбранной новости
    def show_news_detail(self):
        selected_rows = set(index.row() for index in self.newsTable.selectedIndexes())  # Получаем выбранные строки
        if not selected_rows:
            return  # Если ничего не выбрано, выходим из метода

        # Берем первую выбранную строку (если выбрано несколько)
        row = next(iter(selected_rows))

        # Получаем данные из выбранной строки
        source = self.newsTable.item(row, 0).text()
        title = self.newsTable.item(row, 1).text()
        link = self.newsTable.item(row, 2).text()
        date = self.newsTable.item(row, 3).text()

        # Формируем строку с подробной информацией о новости
        detail_text = f"Источник: {source}\nЗаголовок: {title}\nСсылка: {link}\nДата: {date}"
        # Устанавливаем текст в текстовое поле
        self.detailText.setText(detail_text)


class Page2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUpUI()

    def setUpUI(self):
        layout = QVBoxLayout()

        # Добавляем другие элементы на страницу 2
        label = QTextEdit("пока в разработке")
        layout.addWidget(label)

        self.setLayout(layout)


class NewsApp(QWidget):
    def __init__(self):
        super().__init__()

        # Устанавливаем заголовок окна
        self.setWindowTitle("Новости из MySQL")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("icon.png"))

        # Основной вертикальный layout для размещения всех элементов
        main_layout = QVBoxLayout()

        # Стек для страниц
        self.stacked_widget = QStackedWidget()

        # Создаем страницы
        self.page1 = Page1(self)  # Передаем родительский объект
        self.page2 = Page2(self)

        # Добавляем страницы в stacked widget
        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.addWidget(self.page2)

        # Статичный layout с кнопками для переключения
        button_layout = QHBoxLayout()

        # Кнопка для перехода на страницу 1
        self.page1_to_page2_button = QPushButton("Список ресурсов")
        self.page1_to_page2_button.clicked.connect(self.go_to_page2)
        self.page1_to_page2_button.setFixedSize(150, 30)
        button_layout.addWidget(self.page1_to_page2_button)

        # Кнопка для перехода на страницу 2
        self.page2_to_page1_button = QPushButton("База Данных")
        self.page2_to_page1_button.clicked.connect(self.go_to_page1)
        self.page2_to_page1_button.setFixedSize(150, 30)
        button_layout.addWidget(self.page2_to_page1_button)

        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(button_layout)

        # Добавляем стек страниц в главный layout
        main_layout.addWidget(self.stacked_widget)

        # Устанавливаем основной layout для окна
        self.setLayout(main_layout)

    def go_to_page1(self):
        self.stacked_widget.setCurrentWidget(self.page1)

    def go_to_page2(self):
        self.stacked_widget.setCurrentWidget(self.page2)

    def update_table(self, data, source):
        self.page1.newsTable.setRowCount(len(data))
        self.page1.newsTable.setColumnCount(4)
        self.page1.newsTable.setHorizontalHeaderLabels(["Источник", "Заголовок", "Ссылка", "Дата"])
        self.page1.newsTable.setColumnWidth(0, 150)
        self.page1.newsTable.setColumnWidth(1, 350)
        self.page1.newsTable.setColumnWidth(2, 300)
        self.page1.newsTable.setColumnWidth(3, 150)

        for row, news in enumerate(data):
            QTimer.singleShot(row * 10, lambda r=row, n=news: self.add_row(r, n))

    def add_row(self, row, news):
        for col, value in enumerate(news):
            item = QTableWidgetItem(str(value))
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.page1.newsTable.setItem(row, col, item)

    def set_background_image(self, image_path):
        palette = self.palette()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        brush = QBrush(pixmap)
        palette.setBrush(QPalette.ColorRole.Window, brush)
        self.setPalette(palette)


# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewsApp()
    window.show()
    sys.exit(app.exec())
