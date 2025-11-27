import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QGridLayout, QFrame,
                             QPushButton, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QFont

from currency_usd import CurrencyUSD
from currency_eur import CurrencyEUR
from currency_rub import CurrencyRUB


class ExchangeRateThread(QThread):
    """Поток для получения курсов валют из API"""

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.exchangerate-api.com/v4/latest/USD"
        self.rates_updated = None
        self.error_occurred = None

    def set_signals(self, rates_updated, error_occurred):
        """Устанавливает сигналы обратного вызова"""
        self.rates_updated = rates_updated
        self.error_occurred = error_occurred

    def run(self):
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if self.rates_updated:
                    self.rates_updated(data)
            else:
                if self.error_occurred:
                    self.error_occurred(f"Ошибка API: {response.status_code}")
        except requests.exceptions.RequestException as e:
            if self.error_occurred:
                self.error_occurred(f"Ошибка соединения: {str(e)}")


class CurrencyConverter(QMainWindow):
    def __init__(self):
        super().__init__()

        # Создаем объекты валют
        self.usd = CurrencyUSD()
        self.eur = CurrencyEUR()
        self.rub = CurrencyRUB()

        self.currencies = {
            'USD': self.usd,
            'EUR': self.eur,
            'RUB': self.rub
        }

        # Флаг для предотвращения рекурсивного обновления
        self.updating = False
        self.rates_loaded = False

        self.initUI()
        self.connect_currency_signals()
        self.load_exchange_rates()

    def initUI(self):
        self.setWindowTitle('Конвертер валют (Live)')
        self.setFixedSize(700, 700)  # Увеличил высоту для новой кнопки

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(30, 25, 30, 25)

        # Заголовок
        title_label = QLabel('Конвертер валют с актуальными курсами')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setMinimumHeight(50)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 12px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        main_layout.addWidget(title_label)

        # # Прогресс-бар для загрузки
        # self.progress_bar = QProgressBar()
        # self.progress_bar.setVisible(False)
        # self.progress_bar.setFixedHeight(18)
        # self.progress_bar.setStyleSheet("""
        #     QProgressBar {
        #         border: 1px solid #bdc3c7;
        #         border-radius: 4px;
        #         text-align: center;
        #         background-color: white;
        #         font-size: 11px;
        #     }
        #     QProgressBar::chunk {
        #         background-color: #3498db;
        #         border-radius: 3px;
        #     }
        # """)
        # main_layout.addWidget(self.progress_bar)

        # Статус загрузки
        self.status_label = QLabel('Загрузка курсов валют...')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedHeight(20)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 2px;")
        main_layout.addWidget(self.status_label)

        # Сетка для полей ввода
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setVerticalSpacing(18)

        # Увеличиваем ширину колонок
        grid_layout.setColumnMinimumWidth(0, 140)  # Метки
        grid_layout.setColumnMinimumWidth(1, 300)  # Поля ввода

        # Создаем метки с увеличенной шириной
        usd_label = QLabel('Доллары ($):')
        eur_label = QLabel('Евро (€):')
        rub_label = QLabel('Рубли (₽):')

        # Настраиваем метки
        for label in [usd_label, eur_label, rub_label]:
            label.setFixedWidth(130)
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 8px 5px;
                }
            """)

        # Добавляем поля ввода валют
        grid_layout.addWidget(usd_label, 0, 0)
        grid_layout.addWidget(self.usd.create_input_field(), 0, 1)

        grid_layout.addWidget(eur_label, 1, 0)
        grid_layout.addWidget(self.eur.create_input_field(), 1, 1)

        grid_layout.addWidget(rub_label, 2, 0)
        grid_layout.addWidget(self.rub.create_input_field(), 2, 1)

        main_layout.addLayout(grid_layout)

        # Layout для кнопок (обновление и очистка)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(0, 10, 0, 10)

        # Кнопка обновления курсов
        self.update_button = QPushButton('🔄 Обновить курсы')
        self.update_button.setFixedHeight(42)
        self.update_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.update_button.clicked.connect(self.load_exchange_rates)

        # Кнопка очистки полей
        self.clear_button = QPushButton('🗑️ Очистить все')
        self.clear_button.setFixedHeight(42)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.clear_button.clicked.connect(self.clear_all_fields)

        # Добавляем кнопки в layout
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.clear_button)

        main_layout.addLayout(buttons_layout)

        # Информационная панель с курсами
        self.info_frame = self.create_info_panel()
        main_layout.addWidget(self.info_frame)

        # Время последнего обновления
        self.last_update_label = QLabel('Курсы еще не загружены')
        self.last_update_label.setAlignment(Qt.AlignCenter)
        self.last_update_label.setFixedHeight(18)
        self.last_update_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 11px;
                font-style: italic;
                padding: 3px;
            }
        """)
        main_layout.addWidget(self.last_update_label)

        # Подсказка
        hint_label = QLabel('Введите значение в любом поле - остальные обновятся автоматически')
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setFixedHeight(18)
        hint_label.setWordWrap(True)  # Разрешаем перенос текста
        hint_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 16px;
                padding: 3px;
            }
        """)
        main_layout.addWidget(hint_label)

        # Изначально блокируем поля ввода
        self.set_inputs_enabled(False)

    def create_info_panel(self):
        """Создает информационную панель с текущими курсами"""
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.StyledPanel)
        info_frame.setMinimumHeight(130)  # Увеличил высоту
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(6)

        # Заголовок информационной панели (увеличил отступы)
        info_title = QLabel('Текущие курсы:')
        info_title.setFont(QFont('Arial', 13, QFont.Bold))
        info_title.setStyleSheet("""
            QLabel {
                color: #2c3e50; 
                margin-bottom: 8px;
                padding: 5px;
            }
        """)
        info_title.setAlignment(Qt.AlignCenter)
        info_title.setMinimumHeight(25)
        info_layout.addWidget(info_title)

        # Метки для отображения курсов
        self.usd_rates_label = QLabel()
        self.eur_rates_label = QLabel()
        self.rub_rates_label = QLabel()

        for label in [self.usd_rates_label, self.eur_rates_label, self.rub_rates_label]:
            label.setFont(QFont('Arial', 11))
            label.setFixedHeight(22)
            label.setStyleSheet("""
                QLabel {
                    color: #34495e; 
                    padding: 2px;
                    background-color: rgba(255,255,255,0.7);
                    border-radius: 3px;
                    margin: 1px 10px;
                }
            """)
            label.setAlignment(Qt.AlignCenter)
            info_layout.addWidget(label)

        # Добавляем растягивающийся элемент для выравнивания
        info_layout.addStretch(1)

        self.update_rates_display()

        return info_frame

    def connect_currency_signals(self):
        """Подключает сигналы от валют"""
        for currency in self.currencies.values():
            currency.signal.value_changed.connect(self.on_currency_value_changed)

    def set_inputs_enabled(self, enabled):
        """Включает/выключает поля ввода"""
        for currency in self.currencies.values():
            currency.set_enabled(enabled)
        self.update_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)

    def clear_all_fields(self):
        """Очищает все поля ввода"""
        self.updating = True
        try:
            for currency in self.currencies.values():
                currency.clear()
        finally:
            self.updating = False

    def load_exchange_rates(self):
        """Загружает курсы валют из API"""
        # self.progress_bar.setVisible(True)
        self.status_label.setText('Загрузка актуальных курсов...')
        self.set_inputs_enabled(False)
        self.update_button.setEnabled(False)
        self.clear_button.setEnabled(False)

        # Запускаем поток для получения данных
        self.rate_thread = ExchangeRateThread()
        self.rate_thread.set_signals(self.on_rates_updated, self.on_rates_error)
        self.rate_thread.start()

    def on_rates_updated(self, data):
        """Обработчик успешной загрузки курсов"""
        try:
            # Получаем курсы из API ответа
            rates = data['rates']

            # Обновляем курсы валют
            self.eur.set_rate(rates.get('EUR', 0.85))
            self.rub.set_rate(rates.get('RUB', 75.0))

            self.rates_loaded = True

            # Обновляем интерфейс
            self.update_rates_display()
            self.status_label.setText('Курсы успешно загружены!')
            self.status_label.setStyleSheet("color: #27ae60; font-size: 12px; padding: 2px;")
            self.last_update_label.setText(f'Последнее обновление: {data.get("date", "N/A")}')

            # Включаем поля ввода
            self.set_inputs_enabled(True)

        except KeyError as e:
            self.on_rates_error(f"Ошибка формата данных: {str(e)}")
        # finally:
        #     self.progress_bar.setVisible(False)

    def on_rates_error(self, error_message):
        """Обработчик ошибки загрузки курсов"""
        self.status_label.setText(f'Ошибка: {error_message}')
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 12px; padding: 2px;")
        self.last_update_label.setText('Используются курсы по умолчанию')

        # Все равно включаем поля ввода, но с курсами по умолчанию
        self.set_inputs_enabled(True)
        self.update_rates_display()
        # self.progress_bar.setVisible(False)

        QMessageBox.warning(self, 'Ошибка',
                            f'Не удалось загрузить актуальные курсы.\n{error_message}\n\nИспользуются курсы по умолчанию.')

    def update_rates_display(self):
        """Обновляет отображение курсов в информационной панели"""
        self.usd_rates_label.setText(f'1 USD = {self.eur.rate_to_usd:.4f} EUR | {self.rub.rate_to_usd:.4f} RUB')

        # Вычисляем обратные курсы
        eur_to_usd = 1 / self.eur.rate_to_usd if self.eur.rate_to_usd != 0 else 0
        eur_to_rub = self.rub.rate_to_usd / self.eur.rate_to_usd if self.eur.rate_to_usd != 0 else 0
        self.eur_rates_label.setText(f'1 EUR = {eur_to_usd:.4f} USD | {eur_to_rub:.4f} RUB')

        rub_to_usd = 1 / self.rub.rate_to_usd if self.rub.rate_to_usd != 0 else 0
        rub_to_eur = self.eur.rate_to_usd / self.rub.rate_to_usd if self.rub.rate_to_usd != 0 else 0
        self.rub_rates_label.setText(f'1 RUB = {rub_to_usd:.4f} USD | {rub_to_eur:.4f} EUR')

    def on_currency_value_changed(self, source_currency_code, value):
        """Обработчик изменения значения валюты"""
        if self.updating or not self.rates_loaded:
            return

        self.updating = True

        try:
            # Конвертируем в USD
            source_currency = self.currencies[source_currency_code]
            usd_value = source_currency.convert_to_usd(value)

            # Обновляем другие валюты
            for currency_code, currency in self.currencies.items():
                if currency_code != source_currency_code:
                    converted_value = currency.convert_from_usd(usd_value)
                    currency.set_value(converted_value)

        finally:
            self.updating = False


def main():
    app = QApplication(sys.argv)

    # Устанавливаем стиль приложения
    app.setStyle('Fusion')

    converter = CurrencyConverter()
    converter.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()