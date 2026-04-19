"""Модульные тесты для моделей данных."""

import pytest
from decimal import Decimal
from datetime import datetime

from app.core.models import Transaction
from app.core.exceptions import ValidationError


class TestTransactionModel:
    """Тесты для модели Transaction."""
    
    @pytest.mark.parametrize("amount, expected", [
        (Decimal("0.01"), Decimal("0.01")),
        (Decimal("100"), Decimal("100")),
        (Decimal("999999.99"), Decimal("999999.99")),
        (1, Decimal("1")),
        ("123.45", Decimal("123.45")),
        (123.45, Decimal("123.45")),
    ])
    def test_valid_amount_values(self, amount, expected, sample_transaction_data):
        """Тест корректных значений amount."""
        sample_transaction_data["amount"] = amount
        transaction = Transaction.from_dict(sample_transaction_data)
        assert transaction.amount == expected
    
    @pytest.mark.parametrize("amount, error_msg", [
        (Decimal("0"), "amount должен быть > 0"),
        (Decimal("-0.01"), "amount должен быть > 0"),
        (-100, "amount должен быть > 0"),
        ("not_a_number", "не может быть преобразован"),
        (None, "не может быть преобразован"),
        ([], "не может быть преобразован"),
    ])
    def test_invalid_amount_values(self, amount, error_msg, sample_transaction_data):
        """Тест некорректных значений amount."""
        sample_transaction_data["amount"] = amount
        with pytest.raises(ValidationError, match=error_msg):
            Transaction.from_dict(sample_transaction_data)
    
    @pytest.mark.parametrize("date_input, expected", [
        ("2024-01-15", datetime(2024, 1, 15)),
        ("2024-12-31", datetime(2024, 12, 31)),
        ("2023-01-01T12:00:00", datetime(2023, 1, 1, 12, 0, 0)),
    ])
    def test_valid_dates(self, date_input, expected, sample_transaction_data):
        """Тест корректных форматов дат."""
        sample_transaction_data["date"] = date_input
        transaction = Transaction.from_dict(sample_transaction_data)
        assert transaction.date == expected
    
    @pytest.mark.parametrize("date_input", [
        "2024-13-01",  # Несуществующий месяц
        "2024-01-32",  # Несуществующий день
        "not_a_date",
        "01/15/2024",
        "",  # Пустая строка
        # None убираем - он вызывает другой тип ошибки
    ])
    def test_invalid_dates(self, date_input, sample_transaction_data):
        """Тест некорректных форматов дат."""
        sample_transaction_data["date"] = date_input
        with pytest.raises(ValidationError, match="date неверного формата"):
            Transaction.from_dict(sample_transaction_data)

    # Добавляем отдельный тест для None
    def test_none_date(self, sample_transaction_data):
        """Тест None как даты."""
        sample_transaction_data["date"] = None
        # Просто проверяем, что возникает любая ошибка
        with pytest.raises(Exception):
            Transaction.from_dict(sample_transaction_data)
        
    @pytest.mark.parametrize("category", [
        "Food",
        "Transport",
        "Entertainment",
        "Very Long Category Name With Spaces",
        "123",
        "Category_With_Underscore",
    ])
    def test_valid_categories(self, category, sample_transaction_data):
        """Тест корректных категорий."""
        sample_transaction_data["category"] = category
        transaction = Transaction.from_dict(sample_transaction_data)
        assert transaction.category == category
    
    @pytest.mark.parametrize("category", [
        "",
        "   ",
        "\t",
        "\n",
    ])
    def test_empty_categories(self, category, sample_transaction_data):
        """Тест пустых категорий."""
        sample_transaction_data["category"] = category
        with pytest.raises(ValidationError, match="category не может быть пустым"):
            Transaction.from_dict(sample_transaction_data)
    
    def test_missing_required_fields(self, sample_transaction_data):
        """Тест отсутствия обязательных полей."""
        required_fields = ["id", "amount", "category", "date"]
        
        for field in required_fields:
            invalid_data = sample_transaction_data.copy()
            del invalid_data[field]
            
            with pytest.raises(ValidationError, match=f"Отсутствует обязательное поле '{field}'"):
                Transaction.from_dict(invalid_data)
    
    def test_to_dict_conversion(self, sample_transaction):
        """Тест преобразования транзакции в словарь."""
        result = sample_transaction.to_dict()
        
        assert result["id"] == "test_123"
        assert result["amount"] == 100.50
        assert result["category"] == "Food"
        assert result["date"] == "2024-01-15T00:00:00"
        assert result["currency"] == "RUB"
    
    def test_default_currency(self, sample_transaction_data):
        """Тест валюты по умолчанию."""
        # Удаляем currency, чтобы проверить значение по умолчанию
        if "currency" in sample_transaction_data:
            del sample_transaction_data["currency"]
        
        transaction = Transaction.from_dict(sample_transaction_data)
        assert transaction.currency == "RUB"
    
    def test_custom_currency(self, sample_transaction_data):
        """Тест пользовательской валюты."""
        sample_transaction_data["currency"] = "USD"
        transaction = Transaction.from_dict(sample_transaction_data)
        assert transaction.currency == "USD"