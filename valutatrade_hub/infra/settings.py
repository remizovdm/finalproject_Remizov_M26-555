import json

# Singleton реализован через __new__ для простоты и читабельности
class SettingsLoader:
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if not hasattr(self, "_config"):
            with open("config.json", "r") as file:
                self._config = json.load(file)

    def get(self, key: str, default = None):
        return self._config.get(key, default)