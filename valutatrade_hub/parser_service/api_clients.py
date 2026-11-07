
from abc import ABC, abstractmethod

import requests

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import ParserConfig


class BaseApiClient(ABC):

    @abstractmethod
    def fetch_rates(self) -> dict:
        pass


class CoinGeckoClient(BaseApiClient):

    def __init__(self):
        self.config = ParserConfig()

    def fetch_rates(self) -> dict:
        params = {
            "ids": ",".join(self.config.CRYPTO_ID_MAP.values()),
            "vs_currencies": self.config.BASE_CURRENCY.lower()
        }

        try:
            response = requests.get(
                self.config.COINGECKO_URL,
                params=params,
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            rates = {}

            for code, crypto_id in self.config.CRYPTO_ID_MAP.items():
                rate = data[crypto_id][self.config.BASE_CURRENCY.lower()]

                if not isinstance(rate, (int, float)) or rate <= 0:
                    raise ValueError(f"Некорректный курс для {code}")

                pair = f"{code}_{self.config.BASE_CURRENCY}"
                rates[pair] = rate

            return rates

        except (requests.exceptions.RequestException, ValueError, KeyError, TypeError) as e:
            raise ApiRequestError(str(e)) from e


class ExchangeRateApiClient(BaseApiClient):

    def __init__(self):
        self.config = ParserConfig()

    def fetch_rates(self) -> dict:
        if not self.config.EXCHANGERATE_API_KEY:
            raise ApiRequestError("Не задан API-ключ ExchangeRate-API")

        url = (
            f"{self.config.EXCHANGERATE_API_URL}/"
            f"{self.config.EXCHANGERATE_API_KEY}/"
            f"latest/{self.config.BASE_CURRENCY}"
        )

        try:
            response = requests.get(
                url,
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            if data.get("result") != "success":
                raise ApiRequestError(
                    data.get("error-type", "Ошибка ExchangeRate-API")
                )

            rates = {}

            for currency in self.config.FIAT_CURRENCIES:
                rate = data["conversion_rates"][currency]

                if not isinstance(rate, (int, float)) or rate <= 0:
                    raise ValueError(f"Некорректный курс для {currency}")

                pair = f"{currency}_{self.config.BASE_CURRENCY}"
                rates[pair] = 1 / rate

            return rates

        except (requests.exceptions.RequestException, ValueError, KeyError, TypeError) as e:
            raise ApiRequestError(str(e)) from e
