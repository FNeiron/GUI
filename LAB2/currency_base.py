from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt


class CurrencySignal(QObject):
    """Базовый класс сигналов для валют"""
    value_changed = pyqtSignal(str, float)  # (currency_code, value)


class CurrencyBase:
    """Базовый класс для валют"""

    def __init__(self, currency_code, currency_name, currency_symbol):
        self.currency_code = currency_code
        self.currency_name = currency_name
        self.currency_symbol = currency_symbol
        self.signal = CurrencySignal()
        self.input_field = None
        self.rate_to_usd = 1.0

    def create_input_field(self):
        """Создает поле ввода для валюты"""
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(f'Введите {self.currency_name.lower()}')
        self.input_field.setProperty('currency', self.currency_code)

        # Валидатор для чисел с плавающей точкой
        validator = QDoubleValidator(0, 1000000000, 4)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.input_field.setValidator(validator)

        # Стилизация с увеличенной шириной
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px;
                font-size: 16px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                min-width: 280px;
                max-width: 280px;
            }}
            QLineEdit:focus {{
                border-color: {self.get_currency_color()};
                background-color: #f8f9fa;
            }}
            QLineEdit:disabled {{
                background-color: #ecf0f1;
                color: #7f8c8d;
            }}
        """)

        # Фиксируем размер поля ввода
        self.input_field.setMinimumWidth(280)
        self.input_field.setMaximumWidth(280)

        # Подключаем сигнал
        self.input_field.textChanged.connect(self.on_text_changed)

        return self.input_field

    def get_currency_color(self):
        """Возвращает цвет для валюты"""
        colors = {
            'USD': '#27ae60',  # зеленый
            'EUR': '#2980b9',  # синий
            'RUB': '#e74c3c'  # красный
        }
        return colors.get(self.currency_code, '#3498db')

    def on_text_changed(self, text):
        """Обработчик изменения текста"""
        if text and text != '0' and text != '0.0' and text != '0.00':
            try:
                value = float(text)
                self.signal.value_changed.emit(self.currency_code, value)
            except ValueError:
                pass

    def set_rate(self, rate_to_usd):
        """Устанавливает курс к USD"""
        self.rate_to_usd = rate_to_usd

    def convert_to_usd(self, value):
        """Конвертирует значение в USD"""
        return value / self.rate_to_usd if self.rate_to_usd != 0 else 0

    def convert_from_usd(self, usd_value):
        """Конвертирует из USD в эту валюту"""
        return usd_value * self.rate_to_usd

    def clear(self):
        """Очищает поле ввода"""
        if self.input_field:
            self.input_field.clear()

    def set_enabled(self, enabled):
        """Включает/выключает поле ввода"""
        if self.input_field:
            self.input_field.setEnabled(enabled)

    def set_value(self, value):
        """Устанавливает значение в поле ввода"""
        if self.input_field and value != 0:
            self.input_field.setText(f'{value:.4f}')