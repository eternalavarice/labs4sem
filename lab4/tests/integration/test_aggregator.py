"""Интеграционные тесты для агрегатора."""

import pytest
from decimal import Decimal

from app.services.aggregator import CategoryAggregator


class TestCategoryAggregator:
    """Тесты для CategoryAggregator."""
    
    def test_add_single_transaction(self, aggregator, sample_transaction):
        """Тест добавления одной транзакции."""
        aggregator.add_transaction(sample_transaction)
        
        summary = aggregator.get_summary()
        
        assert summary["transaction_count"] == 1
        assert summary["total_amount"] == 100.50
        assert summary["categories"]["Food"] == 100.50
    
    def test_add_multiple_transactions(self, aggregator, complex_transactions):
        """Тест добавления нескольких транзакций."""
        for transaction in complex_transactions:
            aggregator.add_transaction(transaction)
        
        summary = aggregator.get_summary()
        
        assert summary["transaction_count"] == 4
        assert summary["total_amount"] == 100 + 50.50 + 200 + 75.75
        assert summary["categories"]["Food"] == 150.50
        assert summary["categories"]["Transport"] == 200
        assert summary["categories"]["Entertainment"] == 75.75
    
    def test_get_category_sums(self, aggregator, complex_transactions):
        """Тест получения сумм по категориям."""
        for transaction in complex_transactions:
            aggregator.add_transaction(transaction)
        
        sums = aggregator.get_category_sums()
        
        assert sums["Food"] == 150.50
        assert sums["Transport"] == 200
        assert sums["Entertainment"] == 75.75
    
    def test_get_all_transactions(self, aggregator, complex_transactions):
        """Тест получения всех транзакций."""
        for transaction in complex_transactions:
            aggregator.add_transaction(transaction)
        
        transactions = aggregator.get_all_transactions()
        
        assert len(transactions) == 4
        assert all("id" in t for t in transactions)
        assert all("amount" in t for t in transactions)
    
    def test_reset_aggregator(self, aggregator, sample_transaction):
        """Тест сброса агрегатора."""
        aggregator.add_transaction(sample_transaction)
        assert aggregator.transaction_count == 1
        
        aggregator.reset()
        
        assert aggregator.transaction_count == 0
        assert aggregator.get_category_sums() == {}
    
    def test_same_category_aggregation(self, aggregator):
        """Тест агрегации одинаковых категорий."""
        from app.core.models import Transaction
        from datetime import datetime
        
        transactions = [
            Transaction(id="1", amount=Decimal("100"), category="Food", date=datetime.now()),
            Transaction(id="2", amount=Decimal("50"), category="Food", date=datetime.now()),
            Transaction(id="3", amount=Decimal("75"), category="Food", date=datetime.now()),
        ]
        
        for t in transactions:
            aggregator.add_transaction(t)
        
        assert aggregator.get_category_sums()["Food"] == 225