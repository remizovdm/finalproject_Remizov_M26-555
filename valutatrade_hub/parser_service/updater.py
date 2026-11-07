
import logging
from datetime import datetime, timezone

from valutatrade_hub.parser_service.api_clients import (
    CoinGeckoClient,
    ExchangeRateApiClient,
)
from valutatrade_hub.parser_service.storage import RatesStorage
from valutatrade_hub.core.exceptions import ApiRequestError


class RatesUpdater:

    def __init__(self):
        self.clients = [
            ("CoinGecko", CoinGeckoClient()),
            ("ExchangeRate-API", ExchangeRateApiClient())
        ]
        self.storage = RatesStorage()
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
            self.logger.addHandler(handler)

    def run_update(self):
        records = []
        with_errors = False
        self.logger.info("Starting rates update...")

        for source, client in self.clients:
            try:
                rates = client.fetch_rates()
                timestamp = datetime.now(timezone.utc).isoformat()

                for pair, rate in rates.items():
                    from_currency, to_currency = pair.split("_")

                    records.append({
                        "id": f"{pair}_{timestamp}",
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "rate": rate,
                        "timestamp": timestamp,
                        "source": source
                    })

                self.logger.info(
                    "Fetching from %s... OK (%s rates)", source, len(rates)
                    )
                
            except ApiRequestError as e:
                with_errors = True
                self.logger.error("Failed to fetch from %s: %s", source, e)
                

        if records:
            self.logger.info(
                "Writing %s rates to data/rates.json...", len(records)
                )
            self.storage.save_rates(records)

        return len(records), with_errors
