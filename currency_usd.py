from currency_base import CurrencyBase


class CurrencyUSD(CurrencyBase):
    """Класс для работы с долларами США"""

    def __init__(self):
        super().__init__('USD', 'Доллары', '$')
        self.rate_to_usd = 1.0  # Базовая валюта

    def convert_to_usd(self, value):
        """Конвертирует USD в USD (возвращает то же значение)"""
        return value

    def convert_from_usd(self, usd_value):
        """Конвертирует из USD в USD (возвращает то же значение)"""
        return usd_value