"""Базовый класс для всех читателей файлов."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, Any


class BaseFileReader(ABC):
    """Абстрактный базовый класс для чтения файлов."""
    
    @property
    @abstractmethod
    def supported_extensions(self) -> set[str]:
        """Возвращает набор поддерживаемых расширений файлов."""
        pass
    
    @abstractmethod
    def read_records(self, file_path: Path) -> Iterator[dict[str, Any]]:
        """
        Читает записи из файла и возвращает итератор словарей.
        
        Args:
            file_path: Путь к файлу
            
        Yields:
            dict: Словарь с данными записи
            
        Raises:
            DataFormatError: Если файл поврежден или имеет неверный формат
        """
        pass
    
    def can_handle(self, file_path: Path) -> bool:
        """Проверяет, может ли этот читатель обработать файл."""
        return file_path.suffix.lower() in self.supported_extensions