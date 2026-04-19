"""Модуль ввода-вывода данных."""

from app.io.csv_reader import CSVReader
from app.io.json_reader import JSONReader
from app.io.base_reader import BaseFileReader


# Registry Pattern: словарь расширений и читателей
READER_REGISTRY: dict[str, BaseFileReader] = {}

def register_reader(reader: BaseFileReader) -> None:
    """Регистрирует читателя для всех поддерживаемых расширений."""
    for ext in reader.supported_extensions:
        READER_REGISTRY[ext] = reader

def get_reader(file_path: str) -> BaseFileReader | None:
    """Возвращает подходящего читателя для файла."""
    from pathlib import Path
    ext = Path(file_path).suffix.lower()
    return READER_REGISTRY.get(ext)


# Регистрируем стандартных читателей
register_reader(CSVReader())
register_reader(JSONReader())


__all__ = [
    "CSVReader",
    "JSONReader",
    "BaseFileReader",
    "READER_REGISTRY",
    "register_reader",
    "get_reader",
]