"""Общие фикстуры для всех тестов."""

import pytest
import json
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from app.core.models import Transaction
from app.services.validator import TransactionValidator
from app.services.aggregator import CategoryAggregator


@pytest.fixture
def sample_transaction_data():
    """Фикстура с корректными данными транзакции."""
    return {
        "id": "test_123",
        "amount": "100.50",
        "category": "Food",
        "date": "2024-01-15",
        "currency": "RUB"
    }


@pytest.fixture
def sample_transaction():
    """Фикстура с созданной транзакцией."""
    return Transaction(
        id="test_123",
        amount=Decimal("100.50"),
        category="Food",
        date=datetime(2024, 1, 15),
        currency="RUB"
    )


@pytest.fixture
def validator():
    """Фикстура с чистым валидатором."""
    return TransactionValidator()


@pytest.fixture
def aggregator():
    """Фикстура с чистым агрегатором."""
    return CategoryAggregator()


@pytest.fixture
def temp_csv_file(tmp_path):
    """Создает временный CSV файл с заданным содержимым."""
    def _create_csv(filename: str, content: str):
        file_path = tmp_path / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    return _create_csv


@pytest.fixture
def temp_json_file(tmp_path):
    """Создает временный JSON файл с заданным содержимым."""
    def _create_json(filename: str, data):
        file_path = tmp_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path
    return _create_json


@pytest.fixture
def complex_transactions():
    """Фикстура с набором транзакций для агрегации."""
    return [
        Transaction(
            id="1", amount=Decimal("100"), category="Food",
            date=datetime(2024, 1, 1), currency="RUB"
        ),
        Transaction(
            id="2", amount=Decimal("50.50"), category="Food",
            date=datetime(2024, 1, 2), currency="RUB"
        ),
        Transaction(
            id="3", amount=Decimal("200"), category="Transport",
            date=datetime(2024, 1, 3), currency="RUB"
        ),
        Transaction(
            id="4", amount=Decimal("75.75"), category="Entertainment",
            date=datetime(2024, 1, 4), currency="RUB"
        ),
    ]