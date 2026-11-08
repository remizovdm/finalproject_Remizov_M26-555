from abc import ABC, abstractmethod

from .exceptions import CurrencyNotFoundError
from .utils import validate_currency_code


class Currency(ABC):
    """Базовый класс валюты"""
    def __init__(self, name: str, code: str):
        if not isinstance(name, str):
            raise TypeError("Имя валюты должно быть строкой")
        elif name.strip() != "":
            self.name = name
        else:
            raise ValueError("Имя не может быть пустым!")   
        self.code = validate_currency_code(code)

    @abstractmethod
    def get_display_info(self) -> str:
        """Возвращение информации о валюте"""

class FiatCurrency(Currency):
    """Класс фиатной валюты"""
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        """Возвращение информации о фиатной валюте"""
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"

class CryptoCurrency(Currency):
    """Класс криптовалюты"""
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float):
        super().__init__(name, code)
        self.algorithm = algorithm
        self.market_cap = market_cap
    def get_display_info(self) -> str:
        """Возвращение информации о криптовалюте"""
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {self.market_cap})"
    
CURRENCY_REESTR = {
    'USD': FiatCurrency('US Dollar', 'USD', 'United States'),
    'EUR': FiatCurrency('Euro', 'EUR', 'Eurozone'),
    'RUB': FiatCurrency('Russian Ruble', 'RUB', 'Russia'),
    'BTC': CryptoCurrency('Bitcoin', 'BTC', 'SHA-256', 1.12e12),
    'ETH': CryptoCurrency('Ethereum', 'ETH', 'Ethash', 0)
}

def get_currency(code: str) -> Currency:
    """Возвращение валюты по коду"""
    if code in CURRENCY_REESTR:
        return CURRENCY_REESTR[code]
    else:
        raise CurrencyNotFoundError(code)