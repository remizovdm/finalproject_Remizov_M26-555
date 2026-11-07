import os
from dataclasses import dataclass, field


@dataclass
class ParserConfig:
    EXCHANGERATE_API_KEY: str | None = field(
        default_factory=lambda: os.getenv("EXCHANGERATE_API_KEY")
    )

    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    BASE_CURRENCY: str = "USD"

    FIAT_CURRENCIES: tuple = ("EUR", "RUB")
    CRYPTO_CURRENCIES: tuple = ("BTC", "ETH")

    CRYPTO_ID_MAP: dict = field(default_factory=lambda: {
        "BTC": "bitcoin",
        "ETH": "ethereum"
    })

    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    REQUEST_TIMEOUT: int = 10