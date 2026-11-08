import json


class DatabaseManager:
    """Класс чтения и записи в файлы JSON"""
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def read(self, filename:str):
        """Чтение файла JSON"""
        with open(filename, "r") as file:
            data = json.load(file)
            return data

    def write(self, filename, data):
        """Запись файла JSON"""
        with open(filename, "w") as file:
            json.dump(data, file)
