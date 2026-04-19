"""Тесты для кастомных исключений."""

import pytest

from app.core.exceptions import (
    BaseAppError,
    FatalError,
    DataFormatError,
    ValidationError,
    CurrencyMismatchError,
    DuplicateIdError
)


class TestCustomExceptions:
    """Тесты для иерархии исключений."""
    
    def test_exception_hierarchy(self):
        """Тест правильной иерархии наследования."""
        assert issubclass(FatalError, BaseAppError)
        assert issubclass(DataFormatError, BaseAppError)
        assert issubclass(ValidationError, BaseAppError)
        assert issubclass(CurrencyMismatchError, ValidationError)
        assert issubclass(DuplicateIdError, ValidationError)
    
    def test_fatal_error_raising(self):
        """Тест поднятия фатальной ошибки."""
        with pytest.raises(FatalError, match="Конфиг не найден"):
            raise FatalError("Конфиг не найден")
    
    def test_data_format_error_raising(self):
        """Тест поднятия ошибки формата данных."""
        with pytest.raises(DataFormatError, match="Неверный формат CSV"):
            raise DataFormatError("Неверный формат CSV")
    
    def test_validation_error_raising(self):
        """Тест поднятия ошибки валидации."""
        with pytest.raises(ValidationError, match="Сумма не может быть отрицательной"):
            raise ValidationError("Сумма не может быть отрицательной")
    
    def test_currency_mismatch_error_raising(self):
        """Тест поднятия ошибки несоответствия валют."""
        with pytest.raises(CurrencyMismatchError, match="Несоответствие валют"):
            raise CurrencyMismatchError("Несоответствие валют")
    
    def test_duplicate_id_error_raising(self):
        """Тест поднятия ошибки дубликата ID."""
        with pytest.raises(DuplicateIdError, match="ID '123' уже существует"):
            raise DuplicateIdError("ID '123' уже существует")
    
    def test_exception_catching_order(self):
        """Тест порядка перехвата исключений."""
        # ValidationError должен перехватываться до BaseAppError
        try:
            raise ValidationError("Ошибка валидации")
        except ValidationError:
            # Должен перехватиться здесь
            pass
        except BaseAppError:
            pytest.fail("Перехвачен не тот тип исключения")
        
        # CurrencyMismatchError должен перехватываться как ValidationError
        try:
            raise CurrencyMismatchError("Ошибка валют")
        except ValidationError:
            # Должен перехватиться здесь
            pass
        except BaseAppError:
            pytest.fail("Перехвачен не тот тип исключения")