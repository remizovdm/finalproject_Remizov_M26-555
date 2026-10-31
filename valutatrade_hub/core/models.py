from datetime import datetime

import hashlib

import secrets

class User:
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
        return self._user_id, self._username, self._registration_date

    def change_password(self, new_password: str):
        if len(new_password) < 4:
            raise ValueError("Пароль не должен быть короче 4 символов")
        else:
            self._hashed_password = hashlib.sha256((new_password + self._salt).encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        if hashlib.sha256((password  + self._salt).encode()).hexdigest() ==  self._hashed_password:
            return True
        else:
            return False

    def get_user_id(self) -> int:
        return self._user_id

    def get_username(self) -> str:
        return self._username

    def get_hashed_password(self) -> str:
        return self._hashed_password

    def get_salt(self) -> str:
        return self._salt

    def get_registration_date(self) -> datetime:
        return self._registration_date

    def set_username(self, new_username: str):
        if new_username.strip() != "":
            self._username = new_username
        else:
            raise ValueError("Имя не может быть пустым!")


class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self.balance = balance

    def deposit(self, amount: float):
        if amount > 0:
            self.balance = self.balance + amount
        else:
            raise ValueError("Сумма пополнения должна быть положительной!")

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной!")
        elif amount <= self._balance:
            self.balance = self.balance - amount
        else:
            raise ValueError("Сумма снятия не должна превышать текущий баланс")

    def get_balance_info(self) -> str:
        return f"Текущий баланс - {self.currency_code}: {self._balance}"

    @property
    def balance(self) -> float:
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
    def __init__(self, user_id: int, user: User | None = None):
        self._user_id = user_id
        self._user = user
        self._wallets = {}

    def add_currency(self, currency_code: str):
        if currency_code not in self._wallets.keys():
            self._wallets[currency_code] = Wallet(currency_code)

    def get_total_value(self, base_currency: str = "USD", rates: dict | None = None) -> float:
        usd_values = []
        exchange_rates = {
            "USD": 1.0,
            "EUR": 1.1,
            "BTC": 70000.0
            }
        if rates is not None:
            exchange_rates = rates
        for currency, wallet in self._wallets.items():
            result = wallet.balance * exchange_rates[currency]
            usd_values.append(result)
        
        total_usd_value = sum(usd_values)
        converted_total_value = total_usd_value / exchange_rates[base_currency]
        return converted_total_value

    def get_wallet(self, currency_code: str):
        return self._wallets[currency_code]

    @property
    def user(self):
        return self._user

    @property
    def wallets(self):
        return self._wallets.copy()

    
    