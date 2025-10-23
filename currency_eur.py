from currency_base import CurrencyBase


class CurrencyEUR(CurrencyBase):
    """Класс для работы с евро"""

    def __init__(self):
        super().__init__('EUR', 'Евро', '€')
        self.rate_to_usd = 0.85  # Курс по умолчанию