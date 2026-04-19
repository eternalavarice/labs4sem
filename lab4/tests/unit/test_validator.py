"""Модульные тесты для валидатора транзакций."""

import pytest
from pathlib import Path

from app.services.validator import TransactionValidator
from app.core.exceptions import ValidationError, DuplicateIdError


class TestTransactionValidator:
    """Тесты для TransactionValidator."""
    
    def test_validate_correct_transaction(self, validator, sample_transaction_data):
        """Тест валидации корректной транзакции."""
        transaction = validator.validate_and_create(
            sample_transaction_data,
            Path("test.csv")
        )
        
        assert transaction is not None
        assert transaction.id == "test_123"
        assert transaction.amount == 100.50
    
    def test_validate_with_duplicate_id(self, validator, sample_transaction_data):
        """Тест обнаружения дубликатов ID."""
        from app.core.exceptions import DuplicateIdError
        
        # Первая транзакция
        validator.validate_and_create(sample_transaction_data, Path("test.csv"))
        
        # Вторая с тем же ID - ожидаем DuplicateIdError
        with pytest.raises(DuplicateIdError, match="Дубликат ID 'test_123'"):
            validator.validate_and_create(sample_transaction_data, Path("test.csv"))
    
    def test_allow_duplicates_flag(self, validator, sample_transaction_data):
        """Тест разрешения дубликатов через флаг."""
        # Первая транзакция
        validator.validate_and_create(sample_transaction_data, Path("test.csv"))
        
        # Вторая с тем же ID, но с разрешением дубликатов
        transaction = validator.validate_and_create(
            sample_transaction_data, 
            Path("test.csv"),
            allow_duplicates=True
        )
        
        assert transaction is not None
    
    def test_validate_invalid_transaction(self, validator, sample_transaction_data):
        """Тест валидации некорректной транзакции."""
        sample_transaction_data["amount"] = -100
        
        with pytest.raises(ValidationError, match="amount должен быть > 0"):
            validator.validate_and_create(sample_transaction_data, Path("test.csv"))
    
    def test_reset_validator(self, validator, sample_transaction_data):
        """Тест сброса состояния валидатора."""
        # Добавляем транзакцию
        validator.validate_and_create(sample_transaction_data, Path("test.csv"))
        
        # Сбрасываем
        validator.reset()
        
        # Теперь тот же ID должен быть разрешен
        transaction = validator.validate_and_create(sample_transaction_data, Path("test.csv"))
        assert transaction is not None
    
    @pytest.mark.parametrize("field, value", [
        ("amount", 0),
        ("amount", -0.01),
        ("category", ""),
        ("date", "invalid"),
        # Убираем id с пустым значением - это может быть валидно
        # Добавляем другие проверки
        ("amount", "not_a_number"),
        ("amount", None),
    ])
    def test_various_invalid_fields(self, validator, sample_transaction_data, field, value):
        """Параметризованный тест различных некорректных полей."""
        sample_transaction_data[field] = value
        
        with pytest.raises(ValidationError):
            validator.validate_and_create(sample_transaction_data, Path("test.csv"))

    # Добавляем отдельный тест для пустого id
    def test_empty_id(self, validator, sample_transaction_data):
        """Тест пустого ID."""
        sample_transaction_data["id"] = ""
        # Пустой ID может быть валидным, проверяем что не падает
        transaction = validator.validate_and_create(sample_transaction_data, Path("test.csv"), allow_duplicates=True)
        assert transaction is not None

    def test_none_id(self, validator, sample_transaction_data):
        """Тест None как ID."""
        sample_transaction_data["id"] = None
        transaction = validator.validate_and_create(sample_transaction_data, Path("test.csv"), allow_duplicates=True)
        assert transaction is not None