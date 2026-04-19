"""Читатель CSV файлов."""

import csv
from pathlib import Path
from typing import Iterator, Any

from app.io.base_reader import BaseFileReader
from app.core.exceptions import DataFormatError


class CSVReader(BaseFileReader):
    """Читатель CSV файлов с поддержкой различных диалектов."""
    
    @property
    def supported_extensions(self) -> set[str]:
        return {".csv", ".txt"}
    
    def read_records(self, file_path: Path) -> Iterator[dict[str, Any]]:
        """
        Читает CSV файл и возвращает записи в виде словарей.
        
        Args:
            file_path: Путь к CSV файлу
            
        Yields:
            dict: Словарь с данными записи
            
        Raises:
            DataFormatError: Если файл пустой или имеет неверный формат
        """
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                # Проверка на пустой файл
                first_char = f.read(1)
                if not first_char:
                    raise DataFormatError(f"Файл пуст: {file_path}")
                f.seek(0)
                
                # Пробуем определить диалект автоматически
                sample = f.read(1024)
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample)
                except csv.Error:
                    dialect = 'excel'
                
                reader = csv.DictReader(f, dialect=dialect)
                
                if reader.fieldnames is None or len(reader.fieldnames) == 0:
                    raise DataFormatError(f"CSV файл не содержит заголовков: {file_path}")
                
                row_count = 0
                for row_num, row in enumerate(reader, start=2):  # start=2 из-за заголовка
                    row_count += 1
                    # Пропускаем полностью пустые строки
                    if all(v == '' or v is None for v in row.values()):
                        continue
                    
                    # Приводим ключи к нижнему регистру для единообразия
                    normalized_row = {k.lower().strip(): v for k, v in row.items()}
                    yield normalized_row
                
                if row_count == 0:
                    raise DataFormatError(f"CSV файл не содержит данных: {file_path}")
                    
        except (csv.Error, UnicodeDecodeError) as e:
            raise DataFormatError(f"Ошибка парсинга CSV файла {file_path}: {e}") from e
        except PermissionError as e:
            raise DataFormatError(f"Нет доступа к файлу {file_path}: {e}") from e
        except OSError as e:
            raise DataFormatError(f"Ошибка при чтении файла {file_path}: {e}") from e