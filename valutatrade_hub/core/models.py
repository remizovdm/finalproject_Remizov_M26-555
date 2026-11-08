import hashlib
from datetime import datetime

from .exceptions import InsufficientFundsError


class User:
    """Класс пользователя. 
    Содержит имя пользователя и пароль, а также методы для работы с ними"""
    def __init__(self, user_id: int, username: str,
                  hashed_password: str, salt: str, 
                  registration_date: datetime):
        self._user_id = user_id
        if username.strip() != "":
            self._username = username
        else:
            raise ValueError("Имя не может быть пустым!")    
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date


    def get_user_info(self):
        """Возвращение информации о пользователе (ID, имя, дата регистрации)"""
        return self._user_id, self._username, self._registration_date

    def change_password(self, new_password: str):
        """Изменение пароля"""
        if len(new_password) < 4:
            raise ValueError("Пароль не должен быть короче 4 символов")
        else:
            self._hashed_password = hashlib.sha256((new_password + self._salt).encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Проверка пароля"""
        return hashlib.sha256((password + self._salt).encode()).hexdigest() == self._hashed_password

    def get_user_id(self) -> int:
        """Возвращение ID пользователя"""
        return self._user_id

    def get_username(self) -> str:
        """Возвращение имени пользователя"""
        return self._username

    def get_hashed_password(self) -> str:
        """Возвращение хеш-пароля"""
        return self._hashed_password

    def get_salt(self) -> str:
        """Возвращение соли"""
        return self._salt

    def get_registration_date(self) -> datetime:
        """Возвращение даты регистрации"""
        return self._registration_date

    def set_username(self, new_username: str):
        """Установка имени пользователя"""
        if new_username.strip() != "":
            self._username = new_username
        else:
            raise ValueError("Имя не может быть пустым!")


class Wallet:
    """Класс кошелька.
    Содержит код валюты и соответствующий баланс"""
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self.balance = balance

    def deposit(self, amount: float):
        """Добавление средств на счет"""
        if amount > 0:
            self.balance = self.balance + amount
        else:
            raise ValueError("Сумма пополнения должна быть положительной!")

    def withdraw(self, amount: float):
        """Снятие средств со счета"""
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной!")
        elif amount <= self.balance:
            self.balance = self.balance - amount
        else:
            raise InsufficientFundsError(self.currency_code, self.balance, amount)

    def get_balance_info(self) -> str:
        """Получение информации о текущем балансе"""
        return f"Текущий баланс - {self.currency_code}: {self._balance}"

    @property
    def balance(self) -> float:
        """Возвращение баланса"""
        return self._balance

    @balance.setter
    def balance(self, new_balance: float):
        if not isinstance(new_balance, (int, float)):
            raise TypeError("Баланс должен быть числом!")
        elif new_balance < 0:
            raise ValueError("Баланс не должен быть отрицательным!")
        else:
            self._balance = new_balance


class Portfolio:
    """Класс портфеля кошельков"""
    def __init__(self, user_id: int, user: User | None = None):
        self._user_id = user_id
        self._user = user
        self._wallets = {}

    def add_currency(self, currency_code: str):
        """Добавление валюты в портфель"""
        if currency_code not in self._wallets:
            self._wallets[currency_code] = Wallet(currency_code)

    def get_total_value(self, base_currency: str = "USD", rates: dict | None = None) -> float:
        """Общая стоимость портфеля в выбранной валюте"""
        usd_values = []
        if rates is None:
            raise ValueError("Не переданы курсы валют")

        exchange_rates = rates
        for currency, wallet in self._wallets.items():
            result = wallet.balance * exchange_rates[currency]
            usd_values.append(result)
        
        total_usd_value = sum(usd_values)
        converted_total_value = total_usd_value / exchange_rates[base_currency]
        return converted_total_value

    def get_wallet(self, currency_code: str):
        """Возвращение кошелька"""
        return self._wallets[currency_code]

    @property
    def user(self):
        """Возвращение пользователя, которому принадлежит портфель"""
        return self._user

    @property
    def wallets(self):
        """Возвращение копии кошельков"""
        return self._wallets.copy()

    
    