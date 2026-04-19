"""Читатель JSON файлов."""

import json
from pathlib import Path
from typing import Iterator, Any

from app.io.base_reader import BaseFileReader
from app.core.exceptions import DataFormatError


class JSONReader(BaseFileReader):
    """Читатель JSON файлов."""
    
    @property
    def supported_extensions(self) -> set[str]:
        return {".json"}
    
    def read_records(self, file_path: Path) -> Iterator[dict[str, Any]]:
        """
        Читает JSON файл и возвращает записи.
        
        Поддерживает форматы:
        - Массив объектов: [{"id": 1, ...}, ...]
        - Объект с полем records: {"records": [...]}
        
        Args:
            file_path: Путь к JSON файлу
            
        Yields:
            dict: Словарь с данными записи
            
        Raises:
            DataFormatError: Если файл поврежден или имеет неверный формат
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Проверка на пустой файл
                content = f.read()
                if not content.strip():
                    raise DataFormatError(f"JSON файл пуст: {file_path}")
                
                data = json.loads(content)
            
            # Определяем структуру данных
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # Ищем ключи, которые могут содержать массив записей
                records = data.get("records") or data.get("data") or data.get("items")
                if records is None:
                    # Если это одиночный объект, оборачиваем в список
                    records = [data]
            else:
                raise DataFormatError(
                    f"JSON файл должен содержать массив или объект, получен {type(data).__name__}"
                )
            
            if not isinstance(records, list):
                raise DataFormatError(f"Записи должны быть в массиве, получен {type(records).__name__}")
            
            if len(records) == 0:
                raise DataFormatError(f"JSON файл не содержит данных: {file_path}")
            
            for record in records:
                if not isinstance(record, dict):
                    raise DataFormatError(f"Запись должна быть объектом, получен {type(record).__name__}")
                
                # Приводим ключи к нижнему регистру
                normalized_record = {k.lower(): v for k, v in record.items()}
                yield normalized_record
                
        except json.JSONDecodeError as e:
            raise DataFormatError(f"Ошибка парсинга JSON файла {file_path}: {e}") from e
        except PermissionError as e:
            raise DataFormatError(f"Нет доступа к файлу {file_path}: {e}") from e
        except OSError as e:
            raise DataFormatError(f"Ошибка при чтении файла {file_path}: {e}") from e