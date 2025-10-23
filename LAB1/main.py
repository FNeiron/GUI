import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QLabel, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QPainter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Основные настройки окна
        self.setWindowTitle('PyQt5 Приложение')
        self.setMinimumSize(400, 300)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        # Надпись
        self.label = QLabel('Надпись', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
                background-color: rgba(255, 255, 255, 200);
                padding: 20px;
                border: 2px solid #cccccc;
                border-radius: 10px;
            }
        """)

        # Layout для кнопок
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Кнопка 1 - изменение текста
        self.button1 = QPushButton('Изменить текст', self)
        self.button1.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.button1.clicked.connect(self.toggle_text)

        # Кнопка 2 - выбор фона
        self.button2 = QPushButton('Выбрать фон', self)
        self.button2.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.button2.clicked.connect(self.select_background)

        # Добавляем кнопки в layout
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)

        # Добавляем все в основной layout
        layout.addWidget(self.label)
        layout.addLayout(button_layout)
        layout.addStretch(1)

        # Переменная для отслеживания состояния текста
        self.text_changed = False

        # Переменная для хранения текущего фона
        self.current_background = None

        # Получаем размер экрана
        self.screen_size = QApplication.primaryScreen().availableGeometry()

    def toggle_text(self):
        """Изменяет текст между 'Надпись' и 'Текст изменён!'"""
        if not self.text_changed:
            self.label.setText('Текст изменён!')
            self.text_changed = True
        else:
            self.label.setText('Надпись')
            self.text_changed = False

    def select_background(self):
        """Открывает диалог выбора PNG-файла и устанавливает его как фон"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Выберите PNG изображение',
            '',
            'PNG Files (*.png);;All Files (*)'
        )

        if file_path:
            self.set_background_image(file_path)

    def set_background_image(self, image_path):
        """Устанавливает изображение как полупрозрачный фон"""
        try:
            # Загружаем изображение
            pixmap = QPixmap(image_path)

            if pixmap.isNull():
                QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить изображение')
                return

            # Сохраняем ссылку на текущий фон
            self.current_background = pixmap

            # Получаем размеры изображения
            img_width = pixmap.width()
            img_height = pixmap.height()

            # Проверяем размер изображения относительно экрана
            if (img_width <= self.screen_size.width() and
                    img_height <= self.screen_size.height()):
                # Изображение меньше экрана - подстраиваем размер окна
                self.resize(img_width, img_height)
                self.adjustSize()
            else:
                # Изображение больше экрана - максимизируем окно
                self.showMaximized()

            # Создаем полупрозрачную версию изображения (70% прозрачности)
            transparent_pixmap = QPixmap(pixmap.size())
            transparent_pixmap.fill(Qt.transparent)

            # Применяем прозрачность
            from PyQt5.QtGui import QPainter
            painter = QPainter(transparent_pixmap)
            painter.setOpacity(0.7)  # 70% прозрачность
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            # Устанавливаем фон
            palette = self.palette()
            palette.setBrush(QPalette.Window, QBrush(transparent_pixmap))
            self.setPalette(palette)

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Произошла ошибка: {str(e)}')

    def resize_event(self, event):
        """Обработчик изменения размера окна"""
        super().resize_event(event)

        # Если есть установленный фон, перерисовываем его при изменении размера
        if self.current_background:
            # Масштабируем изображение под новый размер окна
            scaled_pixmap = self.current_background.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            # Создаем полупрозрачную версию
            transparent_pixmap = QPixmap(scaled_pixmap.size())
            transparent_pixmap.fill(Qt.transparent)

            painter = QPainter(transparent_pixmap)
            painter.setOpacity(0.7)
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.end()

            # Обновляем фон
            palette = self.palette()
            palette.setBrush(QPalette.Window, QBrush(transparent_pixmap))
            self.setPalette(palette)


def main():
    app = QApplication(sys.argv)

    # Устанавливаем стиль приложения
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()