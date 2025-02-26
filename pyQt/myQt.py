import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, \
    QTableWidgetItem, QTextEdit, QStackedWidget, QSizePolicy, QLineEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QBrush, QPalette
from data.database import get_all_news_rss
from data.database_tg import get_all_news_tg
from data.database_list import get_rss_sources, get_tg_sources, add_tg_source, add_rss_source, remove_rss_source, remove_tg_source

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
        self.parent = parent  # Сохраняем ссылку на родительский объект
        self.setUpUI()

    def setUpUI(self):
        layout = QVBoxLayout()

        # Статичный layout с кнопками для переключения страниц
        button_layout_db = QHBoxLayout()

        self.loadRssButton = QPushButton("Список RSS ресурсов\n")
        self.loadRssButton.clicked.connect(self.load_rss_data)
        self.loadRssButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout_db.addWidget(self.loadRssButton)

        self.loadTgButton = QPushButton("Список TG ресурсов\n")
        self.loadTgButton.clicked.connect(self.load_tg_data)
        self.loadTgButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout_db.addWidget(self.loadTgButton)

        self.loadAllButton = QPushButton("Загрузить все ресурсы\n")
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

        # Размещение кнопок удаления справа от таблицы
        button_layout_delete = QHBoxLayout()

        self.deleteRssButton = QPushButton("Удалить RSS источник")
        self.deleteRssButton.clicked.connect(self.delete_source)
        button_layout_delete.addWidget(self.deleteRssButton)

        self.deleteTgButton = QPushButton("Удалить TG источник")
        self.deleteTgButton.clicked.connect(self.delete_source)
        button_layout_delete.addWidget(self.deleteTgButton)

        layout.addLayout(button_layout_delete)

        # Добавляем поля для ввода и кнопки для добавления источников
        input_layout = QHBoxLayout()

        # Поле для названия источника
        self.sourceNameInput = QLineEdit()
        self.sourceNameInput.setPlaceholderText("Введите название ресурса")
        input_layout.addWidget(self.sourceNameInput)

        # Поле для ввода URL для RSS или TG канала
        self.urlInput = QLineEdit()
        self.urlInput.setPlaceholderText("Введите URL для RSS или Telegram канал")
        input_layout.addWidget(self.urlInput)

        # Кнопка для добавления RSS ресурса
        self.addRssButton = QPushButton("Добавить RSS источник")
        self.addRssButton.clicked.connect(self.add_rss_source)
        input_layout.addWidget(self.addRssButton)

        # Кнопка для добавления TG канала
        self.addTgButton = QPushButton("Добавить TG источник")
        self.addTgButton.clicked.connect(self.add_tg_source)
        input_layout.addWidget(self.addTgButton)

        # Размещаем поля ввода и кнопки внизу
        layout.addLayout(input_layout)

        self.setLayout(layout)

    def load_rss_data(self):
        print("[DEBUG] Подключение к MySQL для RSS...")
        # Получаем новости из RSS
        data = get_rss_sources()
        # Обновляем таблицу данными из RSS
        self.parent.update_table_list(data, "RSS")

    def load_tg_data(self):
        print("[DEBUG] Подключение к MySQL для TG...")
        # Получаем новости из TG
        data = get_tg_sources()
        # Обновляем таблицу данными из TG
        self.parent.update_table_list(data, "TG")

    def load_all_data(self):
        print("[DEBUG] Подключение к MySQL для всех новостей...")
        # Получаем данные из RSS и TG
        rss_data = get_rss_sources()
        tg_data = get_tg_sources()
        # Объединяем данные из обоих источников
        combined_data = rss_data + tg_data
        # Обновляем таблицу с комбинированными данными
        self.parent.update_table_list(combined_data, "Все новости")

    def delete_source(self):
        # Получаем, какая кнопка была нажата (RSS или TG)
        button = self.sender()

        # Получаем выбранную строку
        selected_row = self.newsTable.currentRow()
        if selected_row >= 0:  # Если строка выбрана
            source_name = self.newsTable.item(selected_row, 0).text()  # Получаем имя источника
            url_or_channel = self.newsTable.item(selected_row, 1).text()  # Получаем URL или канал

            # Если была нажата кнопка для удаления RSS источника
            if button == self.deleteRssButton:
                # Удаляем из базы данных RSS источник
                remove_rss_source(source_name)
                # Удаляем строку из таблицы
                self.newsTable.removeRow(selected_row)

            # Если была нажата кнопка для удаления TG источника
            elif button == self.deleteTgButton:
                # Удаляем из базы данных TG источник
                remove_tg_source(source_name)
                # Удаляем строку из таблицы
                self.newsTable.removeRow(selected_row)

    def add_rss_source(self):
        # Получаем название источника и URL из полей ввода
        source_name = self.sourceNameInput.text()
        rss_url = self.urlInput.text()
        if source_name and rss_url:
            # Добавляем RSS источник в базу данных
            add_rss_source(source_name, rss_url)
            self.sourceNameInput.clear()  # Очищаем поле ввода названия
            self.urlInput.clear()  # Очищаем поле ввода URL
            self.load_rss_data()  # Перезагружаем список

    def add_tg_source(self):
        # Получаем название источника и канал из полей ввода
        source_name = self.sourceNameInput.text()
        tg_channel = self.urlInput.text()
        if source_name and tg_channel:
            # Добавляем TG источник в базу данных
            add_tg_source(source_name, tg_channel)
            self.sourceNameInput.clear()  # Очищаем поле ввода названия
            self.urlInput.clear()  # Очищаем поле ввода канала
            self.load_tg_data()  # Перезагружаем список

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

    def update_table_list(self, data_list, source):
        self.page2.newsTable.setRowCount(len(data_list))
        self.page2.newsTable.setColumnCount(2)
        self.page2.newsTable.setHorizontalHeaderLabels(["Источник", "Ссылка"])
        self.page2.newsTable.setColumnWidth(0, 150)
        self.page2.newsTable.setColumnWidth(1, 350)

        for row_list, new_list in enumerate(data_list):
            QTimer.singleShot(row_list * 10, lambda r=row_list, n=new_list: self.add_row_list(r, n))

    def add_row_list(self, row_list, new_list):
        for col, value in enumerate(new_list):
            item = QTableWidgetItem(str(value))
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.page2.newsTable.setItem(row_list, col, item)
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
