import json

import secrets

import hashlib

from datetime import datetime, timezone

from valutatrade_hub.core.models import User, Wallet, Portfolio

from valutatrade_hub.core.utils import validate_amount, validate_currency_code

from .currencies import get_currency

from ..infra.settings import SettingsLoader

from ..decorators import log_action

from .exceptions import InsufficientFundsError, ApiRequestError

from .currencies import get_currency

from valutatrade_hub.parser_service.updater import RatesUpdater

current_user = None

def register(username: str, password: str):
    with open("data/users.json", "r") as file:
        users = json.load(file)
    for user in users:
        if user['username'] == username:
            raise ValueError(f"Имя пользователя '{username}' уже занято")
    user_id = len(users) + 1
    if len(password) < 4:
        raise ValueError("Пароль должен быть не короче 4 символов")
    salt = secrets.token_hex(16)
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
    registration_date = datetime.now()
    new_user = User(user_id, username, hashed_password, salt, registration_date)
    user_data = {
        "user_id": user_id,
        "username": username,
        "hashed_password": hashed_password,
        "salt": salt,
        "registration_date": registration_date.isoformat()
        }
    users.append(user_data)
    with open("data/users.json", "w") as file:
        json.dump(users, file)
    with open("data/portfolios.json", "r") as file:
         portfolios = json.load(file)
    user_portfolios = {
         "user_id": user_id,
         "wallets": {}
         }
    portfolios.append(user_portfolios)
    with open("data/portfolios.json", "w") as file:
        json.dump(portfolios, file)
    print(f"Пользователь '{username}' успешно зарегистрирован (id={user_id}). Войдите: login --username {username} --password ****")

def login(username: str, password: str):
    global current_user
    with open("data/users.json", "r") as file:
        users = json.load(file)
    user_name_list = []
    for user in users:
        user_name_list.append(user['username'])
    if username not in user_name_list:
        raise ValueError(f"Пользователь '{username}' не найден")
    for user in users:
        if user['username'] == username:
            hashed_password = user['hashed_password']
            salt = user['salt']
    if hashlib.sha256((password  + salt).encode()).hexdigest() ==  hashed_password:
        print(f"Вы вошли как '{username}'")
        current_user = username
        return True
    else:
        print("Неверный пароль")
        return False

def show_portfolio(base: str = "USD"):
    if current_user is None:
        raise ValueError("Необходимо войти в систему!")
    with open("data/users.json", "r") as file:
        users = json.load(file)
    for user in users:
        if user['username'] == current_user:
            user_id = user['user_id']
            break
    with open("data/portfolios.json", "r") as file:
        portfolios = json.load(file)
    for user in portfolios:
        if user['user_id'] == user_id:
            wallets = user['wallets']
            break
    with open("data/rates.json", "r") as file:
        rates = json.load(file)
    if base == "USD":
        base_rate = 1
    else:
        base_pair = f"{base}_USD"
        if base_pair not in rates:
            raise ValueError(f"Неизвестная базовая валюта '{base}'")
        base_rate = rates[base_pair]['rate']
    if not wallets:
        print(f"У пользователя {current_user} нет кошельков!")
    else:
        print(f"Портфель пользователя '{current_user}' (база: {base}):")
        total_value = 0

        for currency, balance in wallets.items():
            if currency == "USD":
                rate = 1
            else:
                currency_pair = f"{currency}_USD"
                rate = rates[currency_pair]['rate']

            converted_value = balance['balance'] * rate / base_rate
            total_value = total_value + converted_value
            print(f"- {currency}: {balance['balance']:.4f} → {converted_value:,.2f} {base}")

        print("---------------------------------")
        print(f"ИТОГО: {total_value:,.2f} {base}")

@log_action
def buy(currency: str, amount: float):
    if current_user is None:
        raise ValueError("Необходимо войти в систему!")

    currency = validate_currency_code(currency)
    get_currency(currency)
    amount = validate_amount(amount)

    with open("data/users.json", "r") as file:
        users = json.load(file)
    
    for user in users:
        if user["username"] == current_user:
            user_id = user["user_id"]
            break

    with open("data/portfolios.json", "r") as file:
        portfolios = json.load(file)
    
    for user_portfolio in portfolios:
        if user_portfolio["user_id"] == user_id:
            saved_wallets = user_portfolio["wallets"]
            break

    portfolio = Portfolio(user_id)
    
    for currency_code, wallet_data in saved_wallets.items():
        portfolio.add_currency(currency_code)
        portfolio.get_wallet(currency_code).balance = wallet_data["balance"]

    portfolio.add_currency(currency)
    wallet = portfolio.get_wallet(currency)
    old_balance = wallet.balance

    with open("data/rates.json", "r") as file:
        rates = json.load(file)

    if currency == "USD":
        rate = 1
    else:
        currency_pair = f"{currency}_USD"
        if currency_pair not in rates:
            raise ValueError(f"Не удалось получить курс для {currency}→USD")
        rate = rates[currency_pair]["rate"]

    wallet.deposit(amount)

    user_portfolio["wallets"][currency] = {"balance": wallet.balance}

    with open("data/portfolios.json", "w") as file:
        json.dump(portfolios, file, indent=4)

    print(f"Покупка выполнена: {amount:.4f} {currency} по курсу {rate:.2f} USD/{currency}")
    print("Изменения в портфеле:")
    print(f"- {currency}: было {old_balance:.4f} → стало {wallet.balance:.4f}")
    return {
        "user_id": user_id,
        "rate": rate,
        "base": "USD",
        "old_balance": old_balance,
        "new_balance": wallet.balance
        }

@log_action
def sell(currency: str, amount: float):
    if current_user is None:
        raise ValueError("Необходимо войти в систему!")

    currency = validate_currency_code(currency)
    get_currency(currency)
    amount = validate_amount(amount)

    with open("data/users.json", "r") as file:
        users = json.load(file)

    for user in users:
        if user["username"] == current_user:
            user_id = user["user_id"]
            break

    with open("data/portfolios.json", "r") as file:
        portfolios = json.load(file)

    for user_portfolio in portfolios:
        if user_portfolio["user_id"] == user_id:
            saved_wallets = user_portfolio["wallets"]
            break

    if currency not in saved_wallets:
        raise InsufficientFundsError(currency, 0, amount)

    portfolio = Portfolio(user_id)

    for currency_code, wallet_data in saved_wallets.items():
        portfolio.add_currency(currency_code)
        portfolio.get_wallet(currency_code).balance = wallet_data["balance"]

    wallet = portfolio.get_wallet(currency)
    old_balance = wallet.balance

    if amount > wallet.balance:
        raise InsufficientFundsError(currency, wallet.balance, amount)
    with open("data/rates.json", "r") as file:
        rates = json.load(file)

    if currency == "USD":
        rate = 1
    else:
        currency_pair = f"{currency}_USD"
        if currency_pair not in rates:
            raise ValueError(f"Не удалось получить курс для {currency}→USD")
        rate = rates[currency_pair]["rate"]
    wallet.withdraw(amount)

    user_portfolio["wallets"][currency] = {"balance": wallet.balance}

    with open("data/portfolios.json", "w") as file:
        json.dump(portfolios, file, indent=4)

    print(f"Продажа выполнена: {amount:.4f} {currency} по курсу {rate:.2f} USD/{currency}")
    print("Изменения в портфеле:")
    print(f"- {currency}: было {old_balance:.4f} → стало {wallet.balance:.4f}")
    return {
        "user_id": user_id,
        "rate": rate,
        "base": "USD",
        "old_balance": old_balance,
        "new_balance": wallet.balance
        }

def refresh_rates():
    updater = RatesUpdater()
    updated_count, with_errors = updater.run_update()

    if updated_count == 0:
        raise ApiRequestError("Не удалось обновить курсы валют")

    return updated_count, with_errors



def get_rate(from_currency, to_currency):
    from_currency = validate_currency_code(from_currency)
    to_currency = validate_currency_code(to_currency)
    get_currency(from_currency)
    get_currency(to_currency)

    currency_pair = f"{from_currency}_{to_currency}"
    reverse_pair = f"{to_currency}_{from_currency}"

    for attempt in range(2):
        with open(SettingsLoader().get("RATES_FILE"), "r") as file:
            rates = json.load(file)["pairs"]

        if currency_pair in rates:
            rate = rates[currency_pair]["rate"]
            updated_at = datetime.fromisoformat(rates[currency_pair]["updated_at"])

        elif reverse_pair in rates:
            rate = 1 / rates[reverse_pair]["rate"]
            updated_at = datetime.fromisoformat(rates[reverse_pair]["updated_at"])

        else:
            if attempt == 0:
                refresh_rates()
                continue
            raise ApiRequestError(f"Курс {currency_pair} не найден")

        now = datetime.now(timezone.utc)
        time_difference = now - updated_at

        if time_difference.total_seconds() < SettingsLoader().get("RATES_TTL_SECONDS"):
            return rate, updated_at

        if attempt == 0:
            refresh_rates()

    raise ApiRequestError(f"Не удалось получить актуальный курс {currency_pair}")

