"""Сервис агрегации данных по категориям."""

from decimal import Decimal
from collections import defaultdict
from typing import Any

from app.core.models import Transaction


class CategoryAggregator:
    """Агрегатор сумм по категориям."""
    
    def __init__(self):
        self._categories: dict[str, Decimal] = defaultdict(Decimal)
        self._transactions: list[Transaction] = []
    
    def add_transaction(self, transaction: Transaction) -> None:
        """
        Добавляет транзакцию в агрегатор.
        
        Args:
            transaction: Транзакция для добавления
        """
        self._categories[transaction.category] += transaction.amount
        self._transactions.append(transaction)
    
    def get_category_sums(self) -> dict[str, float]:
        """
        Возвращает суммы по категориям в виде float для JSON.
        
        Returns:
            dict[str, float]: Словарь {категория: сумма}
        """
        return {cat: float(amount) for cat, amount in self._categories.items()}
    
    def get_all_transactions(self) -> list[dict[str, Any]]:
        """
        Возвращает все транзакции в виде словарей.
        
        Returns:
            list[dict]: Список транзакций
        """
        return [t.to_dict() for t in self._transactions]
    
    def get_summary(self) -> dict[str, Any]:
        """
        Возвращает полную сводку.
        
        Returns:
            dict: Сводка с категориями, общей суммой и количеством транзакций
        """
        total = sum(self._categories.values())
        return {
            "categories": self.get_category_sums(),
            "total_amount": float(total),
            "transaction_count": len(self._transactions),
            "transactions": self.get_all_transactions()
        }
    
    @property
    def transaction_count(self) -> int:
        """Количество транзакций."""
        return len(self._transactions)
    
    def reset(self) -> None:
        """Сбрасывает агрегатор."""
        self._categories.clear()
        self._transactions.clear()