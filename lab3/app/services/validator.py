"""Сервис валидации данных."""

from typing import Any, Iterator
from pathlib import Path

from app.core.exceptions import ValidationError, DuplicateIdError
from app.core.models import Transaction


class TransactionValidator:
    """Валидатор транзакций."""
    
    def __init__(self):
        self._processed_ids: set[str] = set()
    
    def validate_and_create(
        self, 
        record: dict[str, Any], 
        file_path: Path,
        allow_duplicates: bool = False
    ) -> Transaction | None:
        """
        Валидирует запись и создает транзакцию.
        
        Args:
            record: Словарь с данными записи
            file_path: Путь к файлу (для контекста в ошибках)
            allow_duplicates: Разрешить дубликаты ID
            
        Returns:
            Transaction | None: Транзакция или None при ошибке валидации
            
        Raises:
            ValidationError: При ошибках валидации
        """
        try:
            # Создаем транзакцию (включает базовую валидацию)
            transaction = Transaction.from_dict(record)
            
            # Проверка на дубликаты ID
            if not allow_duplicates and transaction.id in self._processed_ids:
                raise DuplicateIdError(
                    f"Дубликат ID '{transaction.id}' в файле {file_path.name}"
                )
            
            # Сохраняем ID для отслеживания дубликатов
            self._processed_ids.add(transaction.id)
            
            return transaction
            
        except ValidationError as e:
            # Добавляем контекст файла и перевыбрасываем
            raise ValidationError(f"[{file_path.name}] {str(e)}") from e
    
    def reset(self) -> None:
        """Сбрасывает состояние валидатора."""
        self._processed_ids.clear()