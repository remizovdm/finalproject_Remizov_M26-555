def validate_amount(amount: float) -> float:
    """Проверка суммы (должна быть положительной)"""
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    return amount

def validate_currency_code(currency_code: str) -> str:
    """Проверка кода валюты на соответствие необходимым требованиям"""
    if not isinstance(currency_code, str):
        raise TypeError("Код валюты должен быть строкой")
    if currency_code.strip() == "":
        raise ValueError("Код валюты не может быть пустым")
    elif currency_code.isupper() == False:
        raise ValueError("Код валюты должен быть в верхнем регистре")
    elif len(currency_code) < 2:
        raise ValueError("Длина кода валюты не должна быть меньше 2 символов")
    elif len(currency_code) > 5:
        raise ValueError("Длина кода валюты не должна быть больше 5 символов")
    elif " " in currency_code:
        raise ValueError("Код валюты не должен содержать пробелов")
    else:
        return currency_code