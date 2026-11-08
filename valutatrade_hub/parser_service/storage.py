
import json
import os
import tempfile
from pathlib import Path

from valutatrade_hub.parser_service.config import ParserConfig


class RatesStorage:
    """Класс для хранения курсов валют"""

    def __init__(self):
        config = ParserConfig()
        self.rates_path = Path(config.RATES_FILE_PATH)
        self.history_path = Path(config.HISTORY_FILE_PATH)

    def read_json(self, path, default):
        """Чтение хранилища курсов"""
        if not path.exists():
            return default

        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def write_json(self, path, data):
        """Запись в хранилище курсов"""
        path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                delete=False
            ) as file:
                temp_path = file.name
                json.dump(data, file, ensure_ascii=False, indent=4)

            os.replace(temp_path, path)

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    def save_rates(self, records):
        """Сохранение курсов"""
        cache = self.read_json(self.rates_path, {"pairs": {}})
        history = self.read_json(self.history_path, [])
        
        cache.setdefault("pairs", {})

        existing_ids = {record["id"] for record in history}

        for record in records:
            if record["id"] not in existing_ids:
                history.append(record)
                existing_ids.add(record["id"])

            pair = f"{record['from_currency']}_{record['to_currency']}"
            old = cache["pairs"].get(pair)

            if old is None or record["timestamp"] > old["updated_at"]:
                cache["pairs"][pair] = {
                    "rate": record["rate"],
                    "updated_at": record["timestamp"],
                    "source": record["source"]
                }

        if records:
            cache["last_refresh"] = max(
                record["timestamp"] for record in records
            )

        self.write_json(self.history_path, history)
        self.write_json(self.rates_path, cache)
