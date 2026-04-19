"""Интеграционные тесты для процессора данных."""

import pytest
import json
from pathlib import Path

from app.services.processor import DataProcessor
from app.core.exceptions import FatalError


class TestDataProcessorIntegration:
    """Тесты для DataProcessor."""
    
    def test_process_valid_csv_file(self, tmp_path):
        """Тест обработки валидного CSV файла."""
        csv_content = """id,amount,category,date
1,100.50,Food,2024-01-15
2,200.00,Transport,2024-01-16
"""
        file_path = tmp_path / "test.csv"
        file_path.write_text(csv_content, encoding='utf-8')
        
        processor = DataProcessor()
        processor.process_directory(tmp_path)
        
        report = processor.get_report()
        
        assert report["summary"]["processed_files"] == 1
        assert report["summary"]["skipped_files"] == 0
        assert report["summary"]["total_transactions"] == 2
    
    def test_process_mixed_files(self, tmp_path):
        """Тест обработки смешанных файлов (хороших и плохих)."""
        # Хороший CSV
        good_csv = tmp_path / "good.csv"
        good_csv.write_text("id,amount,category,date\n1,100,Food,2024-01-15", encoding='utf-8')
        
        # Плохой CSV (пустой)
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("", encoding='utf-8')
        
        # Хороший JSON
        good_json = tmp_path / "good.json"
        with open(good_json, 'w') as f:
            json.dump([{"id": "2", "amount": 200, "category": "Transport", "date": "2024-01-16"}], f)
        
        processor = DataProcessor()
        processor.process_directory(tmp_path)
        
        report = processor.get_report()
        
        # Должен быть 1 успешный файл (good.csv), good.json тоже успешен
        # bad.csv должен быть пропущен
        assert report["summary"]["processed_files"] == 2
        assert report["summary"]["skipped_files"] == 1
        assert report["summary"]["total_transactions"] == 2
    
    def test_process_with_invalid_records(self, tmp_path):
        """Тест обработки файла с частично невалидными записями."""
        csv_content = """id,amount,category,date
1,100,Food,2024-01-15
2,-50,Transport,2024-01-16
3,75,Entertainment,2024-01-17
"""
        file_path = tmp_path / "test.csv"
        file_path.write_text(csv_content, encoding='utf-8')
        
        processor = DataProcessor()
        processor.process_directory(tmp_path)
        
        report = processor.get_report()
        
        # Должны обработаться 2 валидные записи из 3
        assert report["summary"]["total_transactions"] == 2
        assert report["summary"]["total_errors"] == 1
    
    def test_process_nonexistent_directory(self):
        """Тест обработки несуществующей директории."""
        processor = DataProcessor()
        
        with pytest.raises(FatalError, match="Директория не существует"):
            processor.process_directory(Path("/nonexistent/directory"))
    
    def test_process_empty_directory(self, tmp_path):
        """Тест обработки пустой директории."""
        processor = DataProcessor()
        processor.process_directory(tmp_path)
        
        report = processor.get_report()
        
        assert report["summary"]["processed_files"] == 0
        assert report["summary"]["skipped_files"] == 0
    
    def test_duplicate_ids_across_files(self, tmp_path):
        """Тест дубликатов ID в разных файлах."""
        # Первый файл
        file1 = tmp_path / "file1.csv"
        file1.write_text("id,amount,category,date\n1,100,Food,2024-01-15", encoding='utf-8')
        
        # Второй файл с тем же ID
        file2 = tmp_path / "file2.csv"
        file2.write_text("id,amount,category,date\n1,200,Transport,2024-01-16", encoding='utf-8')
        
        processor = DataProcessor()
        processor.process_directory(tmp_path)
        
        report = processor.get_report()
        
        # Должна быть только первая транзакция, вторая - дубликат
        assert report["summary"]["total_transactions"] == 1
        assert report["summary"]["total_errors"] == 1
    
    def test_reset_processor(self, tmp_path):
        """Тест сброса состояния процессора."""
        # Обрабатываем файл
        csv_content = "id,amount,category,date\n1,100,Food,2024-01-15"
        file_path = tmp_path / "test.csv"
        file_path.write_text(csv_content, encoding='utf-8')
        
        processor = DataProcessor()
        processor.process_directory(tmp_path)
        
        assert processor.aggregator.transaction_count == 1
        
        # Сбрасываем
        processor.reset()
        
        assert processor.aggregator.transaction_count == 0
        assert len(processor.errors) == 0
    
    def test_unsupported_file_format(self, tmp_path):
        """Тест неподдерживаемого формата файла."""
        file_path = tmp_path / "test.xml"
        file_path.write_text("<data></data>", encoding='utf-8')
        
        processor = DataProcessor()
        processor.process_directory(tmp_path)
        
        report = processor.get_report()
        
        assert report["summary"]["skipped_files"] == 1
        assert len(report["errors"]) == 1
        assert "Неподдерживаемое расширение" in report["errors"][0]["message"]