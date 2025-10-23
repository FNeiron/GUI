from currency_base import CurrencyBase


class CurrencyRUB(CurrencyBase):
    """Класс для работы с рублями"""

    def __init__(self):
        super().__init__('RUB', 'Рубли', '₽')
        self.rate_to_usd = 75.0  # Курс по умолчанию