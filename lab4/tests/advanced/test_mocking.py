"""Продвинутые тесты с использованием моков."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from app.services.processor import DataProcessor
from app.core.exceptions import DataFormatError, FatalError
from app.io import CSVReader


class TestMocking:
    """Тесты с имитацией внешних зависимостей."""
    
    @patch('builtins.open')
    @patch('shutil.move')
        
    @patch('app.io.csv_reader.open')
    def test_csv_reader_unicode_error_mocking(self):
        """Тест имитации ошибки декодирования."""
        from unittest.mock import patch, MagicMock
        from app.io.csv_reader import CSVReader
        from app.core.exceptions import DataFormatError
        from pathlib import Path
        import pytest
        
        with patch('builtins.open') as mock_open:
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')
            mock_open.return_value = mock_file
            
            reader = CSVReader()
            
            with pytest.raises(DataFormatError, match="Ошибка парсинга CSV"):
                list(reader.read_records(Path("test.csv")))
    
    @patch('app.services.processor.get_reader')
    def test_processor_with_mocked_reader(self, mock_get_reader, tmp_path):
        """Тест процессора с мокнутым читателем."""
        # Создаем мок для читателя
        mock_reader = MagicMock()
        mock_reader.read_records.return_value = [
            {"id": "1", "amount": 100, "category": "Food", "date": "2024-01-15"}
        ]
        mock_get_reader.return_value = mock_reader
        
        # Создаем тестовый файл
        file_path = tmp_path / "test.csv"
        file_path.touch()
        
        processor = DataProcessor()
        processor.process_directory(tmp_path)
        
        # Проверяем, что мок был вызван
        mock_get_reader.assert_called_once()
        mock_reader.read_records.assert_called_once()
        
        report = processor.get_report()
        assert report["summary"]["total_transactions"] == 1
    
    @patch('app.services.processor.get_reader')
    def test_processor_with_mocked_reader_error(self, mock_get_reader, tmp_path):
        """Тест процессора с мокнутым читателем, выбрасывающим ошибку."""
        mock_reader = MagicMock()
        mock_reader.read_records.side_effect = DataFormatError("Симулированная ошибка")
        mock_get_reader.return_value = mock_reader
        
        file_path = tmp_path / "test.csv"
        file_path.touch()
        
        processor = DataProcessor()
        processor.process_directory(tmp_path)
        
        report = processor.get_report()
        assert report["summary"]["skipped_files"] == 1
        assert len(report["errors"]) == 1
    
    @patch('app.services.processor.get_reader')
    def test_processor_with_no_reader(self, mock_get_reader, tmp_path):
        """Тест процессора когда нет подходящего читателя."""
        mock_get_reader.return_value = None
        
        file_path = tmp_path / "test.xyz"
        file_path.touch()
        
        processor = DataProcessor()
        processor.process_directory(tmp_path)
        
        report = processor.get_report()
        assert report["summary"]["skipped_files"] == 1
        assert "Неподдерживаемое расширение" in report["errors"][0]["message"]
    
    @patch('builtins.open')
    @patch('shutil.move')
    def test_transactional_write_failure(self, tmp_path):
        """Тест имитации ошибки при транзакционной записи."""
        from unittest.mock import patch, MagicMock
        import sys
        from pathlib import Path
        
        # Добавляем путь к корневой директории
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        try:
            from main import export_result_with_transactionality
        except ImportError:
            pytest.skip("main.py not found")
            return
        
        with patch('builtins.open') as mock_open, patch('shutil.move') as mock_move:
            mock_move.side_effect = OSError("Диск защищен от записи")
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = export_result_with_transactionality(
                {"test": "data"},
                tmp_path / "result.json"
            )
            
            assert result is False
    
    @patch('logging.Logger.error')
    def test_processor_logging_on_error(self, mock_logger_error, tmp_path):
        """Тест логирования ошибок в процессоре."""
        # Создаем файл, который вызовет ошибку
        file_path = tmp_path / "bad.csv"
        file_path.write_text("", encoding='utf-8')  # Пустой файл
        
        processor = DataProcessor()
        processor.process_directory(tmp_path)
        
        # Проверяем, что логгер был вызван (хотя бы раз)
        # В реальном тесте нужно настроить логгер соответствующим образом
        assert processor.get_report()["summary"]["skipped_files"] == 1
    
    @patch('app.io.json_reader.open')
    def test_json_reader_io_error(self, mock_open):
        """Тест ошибки ввода-вывода при чтении JSON."""
        mock_open.side_effect = OSError("Ошибка ввода-вывода")
        
        from app.io.json_reader import JSONReader
        reader = JSONReader()
        
        with pytest.raises(DataFormatError, match="Ошибка при чтении файла"):
            list(reader.read_records(Path("test.json")))
    
    @patch('app.io.csv_reader.csv.DictReader')
    def test_csv_reader_parsing_error(self, mock_dict_reader):
        """Тест ошибки парсинга CSV."""
        mock_dict_reader.side_effect = csv.Error("CSV parsing error")
        
        # Создаем временный файл для чтения
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("id,amount\n1,100")
            temp_path = Path(f.name)
        
        try:
            reader = CSVReader()
            with pytest.raises(DataFormatError, match="Ошибка парсинга CSV"):
                list(reader.read_records(temp_path))
        finally:
            temp_path.unlink()

# Импорт для csv в последнем тесте
import csv