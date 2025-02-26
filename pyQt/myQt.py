import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, \
    QTableWidgetItem, QTextEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QColor, QPalette, QPixmap, QBrush
from data.database import get_all_news_rss
from data.database_tg import get_all_news_tg


class NewsApp(QWidget):
    def __init__(self):
        super().__init__()

        # Устанавливаем заголовок окна
        self.setWindowTitle("Новости из MySQL")
        # Устанавливаем начальный размер окна
        self.setGeometry(100, 100, 1000, 700)  # Увеличиваем размер окна
        # Устанавливаем минимальный размер окна для того, чтобы оно могло быть растянуто
        self.setMinimumSize(800, 600)
        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon("icon.png"))

        # Основной вертикальный layout для размещения всех элементов
        layout = QVBoxLayout()

        # Создаем горизонтальный layout для кнопок
        button_layout = QHBoxLayout()

        # Кнопка для загрузки новостей с RSS
        self.loadRssButton = QPushButton("Прочесть новости с RSS ленты")
        # Подключаем обработчик нажатия кнопки
        self.loadRssButton.clicked.connect(self.load_rss_data)
        # Добавляем кнопку в layout
        button_layout.addWidget(self.loadRssButton)

        # Кнопка для загрузки новостей с TG каналов
        self.loadTgButton = QPushButton("Прочесть новости с TG каналов")
        self.loadTgButton.clicked.connect(self.load_tg_data)
        button_layout.addWidget(self.loadTgButton)

        # Кнопка для загрузки всех новостей
        self.loadAllButton = QPushButton("Загрузить все новости")
        self.loadAllButton.clicked.connect(self.load_all_data)
        button_layout.addWidget(self.loadAllButton)

        # Добавляем layout с кнопками в основной вертикальный layout
        layout.addLayout(button_layout)

        # Создаем таблицу для отображения новостей
        self.newsTable = QTableWidget()
        # Настроим поведение таблицы: при выборе строки выделяется вся строка
        self.newsTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Включаем сортировку по столбцам
        self.newsTable.setSortingEnabled(True)
        layout.addWidget(self.newsTable)

        # Создаем текстовое поле для отображения подробной информации о новости
        self.detailText = QTextEdit()
        # Делаем текстовое поле доступным только для чтения
        self.detailText.setReadOnly(True)
        layout.addWidget(self.detailText)

        # Устанавливаем основной layout для окна
        self.setLayout(layout)

        # Подключаем обработчик события выбора строки в таблице
        self.newsTable.itemSelectionChanged.connect(self.show_news_detail)

        """
        Устанавливает фоновое изображение для окна приложения.
        Используется QPalette и QBrush для установки изображения в качестве фона.
        """
    def set_background_image(self, image_path):
        palette = self.palette()
        pixmap = QPixmap(image_path)
        # Масштабируем изображение, чтобы оно подходило под размер окна
        pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        # Создаем QBrush с изображением
        brush = QBrush(pixmap)
        # Устанавливаем QBrush как фон для окна
        palette.setBrush(QPalette.ColorRole.Window, brush)
        self.setPalette(palette)

        """Загружает новости из MySQL RSS и обновляет таблицу"""
    def load_rss_data(self):
        print("[DEBUG] Подключение к MySQL для RSS...")
        # Получаем новости из RSS
        data = get_all_news_rss()
        # Обновляем таблицу данными из RSS
        self.update_table(data, "RSS")

        """Загружает новости из MySQL TG и обновляет таблицу"""
    def load_tg_data(self):
        print("[DEBUG] Подключение к MySQL для TG...")
        # Получаем новости из TG
        data = get_all_news_tg()
        # Обновляем таблицу данными из TG
        self.update_table(data, "TG")

        """Загружает все новости из MySQL (RSS + TG) и обновляет таблицу"""
    def load_all_data(self):
        print("[DEBUG] Подключение к MySQL для всех новостей...")
        # Получаем данные из RSS и TG
        rss_data = get_all_news_rss()
        tg_data = get_all_news_tg()
        # Объединяем данные из обоих источников
        combined_data = rss_data + tg_data
        # Обновляем таблицу с комбинированными данными
        self.update_table(combined_data, "Все новости")

        """
        Обновляет таблицу с новостями.
        Устанавливает количество строк, столбцов и заполняет таблицу данными.
        """
    def update_table(self, data, source):
        if not data:
            print(f"[DEBUG] Данных нет для {source}, таблица остается пустой")
            return

        # Устанавливаем количество строк в таблице в зависимости от данных
        self.newsTable.setRowCount(len(data))

        # Устанавливаем количество столбцов и их заголовки
        self.newsTable.setColumnCount(4)
        self.newsTable.setHorizontalHeaderLabels(["Источник", "Заголовок", "Ссылка", "Дата"])

        # Устанавливаем ширину столбцов для удобства чтения
        self.newsTable.setColumnWidth(0, 150)  # Источник
        self.newsTable.setColumnWidth(1, 350)  # Заголовок
        self.newsTable.setColumnWidth(2, 300)  # Ссылка
        self.newsTable.setColumnWidth(3, 150)  # Дата

        # Используем QTimer для того, чтобы добавить строки с небольшими задержками
        for row, news in enumerate(data):
            # Используем QTimer для добавления строк поочередно
            QTimer.singleShot(row * 10, lambda r=row, n=news: self.add_row(r, n))

        print(f"[DEBUG] Загружено {len(data)} записей из {source}")

        """
        Добавляет строку с новостью в таблицу.
        Каждый элемент новости добавляется в соответствующий столбец.
        """
    def add_row(self, row, news):
        for col, value in enumerate(news):
            item = QTableWidgetItem(str(value))
            # Устанавливаем флаги, чтобы элемент был доступен для выделения и редактирования
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.newsTable.setItem(row, col, item)

        """
        Отображает подробную информацию о выбранной новости.
        Когда пользователь выбирает строку в таблице, отображается информация в текстовом поле.
        """
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


if __name__ == "__main__":
    # Создаем приложение
    app = QApplication(sys.argv)
    # Создаем окно приложения
    window = NewsApp()
    # Отображаем окно
    window.show()
    # Запускаем главный цикл приложения
    sys.exit(app.exec())
