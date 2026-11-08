class CurrencyNotFoundError(Exception):
    """Исключение для неизвестной валюты"""
    def __init__(self, code:str):
        super().__init__(f"Неизвестная валюта '{code}'")

class InsufficientFundsError(Exception):
    """Исключение в случае недостаточного количества средств"""
    def __init__(self, code:str, available:float, required:float):
        super().__init__(f"Недостаточно средств: доступно {available} {code}, требуется {required} {code}")

class ApiRequestError(Exception):
    """Исключение для ошибки API-запроса"""
    def __init__(self, reason:str):
        super().__init__(f"Ошибка при обращении к внешнему API: {reason}")
