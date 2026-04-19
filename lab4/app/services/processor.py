"""Главный процессор для обработки файлов."""

import logging
from pathlib import Path
from typing import Any

from app.core.exceptions import DataFormatError, ValidationError, FatalError
from app.services.validator import TransactionValidator
from app.services.aggregator import CategoryAggregator
from app.io import get_reader


logger = logging.getLogger(__name__)


class ProcessingErrorInfo:
    """Информация об ошибке обработки файла."""
    
    def __init__(self, file_path: Path, error: Exception, record: dict[str, Any] | None = None):
        self.file_path = file_path
        self.error = error
        self.record = record
        self.error_type = type(error).__name__
    
    def to_dict(self) -> dict[str, Any]:
        """Преобразует в словарь для отчета."""
        return {
            "file": str(self.file_path),
            "error_type": self.error_type,
            "message": str(self.error),
            "record": self.record
        }


class DataProcessor:
    """Основной процессор для обработки всех файлов."""
    
    def __init__(self):
        self.validator = TransactionValidator()
        self.aggregator = CategoryAggregator()
        self.errors: list[ProcessingErrorInfo] = []
        self.processed_files: set[Path] = set()
        self.skipped_files: set[Path] = set()
    
    def process_directory(self, data_dir: Path) -> None:
        """
        Обрабатывает все поддерживаемые файлы в директории.
        
        Args:
            data_dir: Путь к директории с файлами
            
        Raises:
            FatalError: Если директория не существует
        """
        if not data_dir.exists():
            raise FatalError(f"Директория не существует: {data_dir}")
        
        if not data_dir.is_dir():
            raise FatalError(f"Путь не является директорией: {data_dir}")
        
        # Сброс состояния перед обработкой
        self.reset()
        
        # Сканируем все файлы
        files = list(data_dir.iterdir())
        if not files:
            logger.warning(f"Директория {data_dir} пуста")
            return
        
        for file_path in files:
            if file_path.is_file():
                self._process_file(file_path)
        
        self._log_summary()
    
    def _process_file(self, file_path: Path) -> None:
        """
        Обрабатывает один файл.
        
        Реализует принцип Graceful Degradation: ошибки в одном файле не останавливают обработку других.
        """
        # Проверяем, есть ли читатель для этого файла
        reader = get_reader(file_path)
        if reader is None:
            logger.warning(f"Неподдерживаемый формат файла: {file_path.suffix}")
            self.skipped_files.add(file_path)
            self.errors.append(ProcessingErrorInfo(
                file_path, 
                DataFormatError(f"Неподдерживаемое расширение: {file_path.suffix}")
            ))
            return
        
        logger.info(f"Обработка файла: {file_path.name}")
        
        try:
            records = list(reader.read_records(file_path))
            file_record_count = 0
            file_error_count = 0
            
            for record in records:
                try:
                    transaction = self.validator.validate_and_create(record, file_path)
                    if transaction:
                        self.aggregator.add_transaction(transaction)
                        file_record_count += 1
                except ValidationError as e:
                    file_error_count += 1
                    self.errors.append(ProcessingErrorInfo(file_path, e, record))
                    logger.error(f"Ошибка валидации в {file_path.name}: {e}")
            
            if file_record_count > 0 or file_error_count == 0:
                self.processed_files.add(file_path)
                logger.info(
                    f"Файл {file_path.name}: обработано {file_record_count} записей, "
                    f"ошибок {file_error_count}"
                )
            else:
                # Если нет ни одной успешной записи, считаем файл проблемным
                self.skipped_files.add(file_path)
                
        except DataFormatError as e:
            logger.error(f"Ошибка формата файла {file_path.name}: {e}")
            self.skipped_files.add(file_path)
            self.errors.append(ProcessingErrorInfo(file_path, e))
    
    def _log_summary(self) -> None:
        """Логирует сводку по обработке."""
        total_files = len(self.processed_files) + len(self.skipped_files)
        logger.info("=" * 50)
        logger.info("СВОДКА ОБРАБОТКИ:")
        logger.info(f"  Всего файлов: {total_files}")
        logger.info(f"  Успешно обработано: {len(self.processed_files)}")
        logger.info(f"  Пропущено/с ошибками: {len(self.skipped_files)}")
        logger.info(f"  Всего транзакций: {self.aggregator.transaction_count}")
        logger.info(f"  Всего ошибок: {len(self.errors)}")
        
        if self.errors:
            logger.info("  Ошибки:")
            for err in self.errors[:10]:  # Показываем первые 10
                logger.info(f"    - {err.file_path.name}: {err.error_type} - {err.error}")
            if len(self.errors) > 10:
                logger.info(f"    ... и еще {len(self.errors) - 10} ошибок")
    
    def get_report(self) -> dict[str, Any]:
        """
        Возвращает полный отчет об обработке.
        
        Returns:
            dict: Отчет с результатами обработки
        """
        return {
            "summary": {
                "processed_files": len(self.processed_files),
                "skipped_files": len(self.skipped_files),
                "total_files": len(self.processed_files) + len(self.skipped_files),
                "total_transactions": self.aggregator.transaction_count,
                "total_errors": len(self.errors)
            },
            "processed_files_list": [str(p) for p in self.processed_files],
            "skipped_files_list": [str(p) for p in self.skipped_files],
            "errors": [e.to_dict() for e in self.errors],
            "aggregated_data": self.aggregator.get_summary()
        }
    
    def reset(self) -> None:
        """Сбрасывает состояние процессора."""
        self.validator.reset()
        self.aggregator.reset()
        self.errors.clear()
        self.processed_files.clear()
        self.skipped_files.clear()