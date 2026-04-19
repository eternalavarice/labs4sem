"""Модели данных для финансовых транзакций."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from decimal import Decimal, InvalidOperation


@dataclass
class Transaction:
    """Модель финансовой транзакции."""
    
    id: str
    amount: Decimal
    category: str
    date: datetime
    currency: str = "RUB"
    raw_data: dict[str, Any] | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Transaction":
        """
        Создает транзакцию из словаря с валидацией типов.
        
        Args:
            data: Словарь с полями id, amount, category, date
            
        Returns:
            Transaction: Созданная транзакция
            
        Raises:
            ValidationError: Если данные не проходят валидацию
        """
        from app.core.exceptions import ValidationError
        
        # Проверка наличия обязательных полей
        required_fields = ["id", "amount", "category", "date"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(
                    f"Отсутствует обязательное поле '{field}' в записи: {data}"
                )
        
        # Валидация amount
        try:
            amount = Decimal(str(data["amount"]))
            if amount <= 0:
                raise ValidationError(
                    f"amount должен быть > 0, получено: {amount} (id: {data['id']})"
                )
        except (InvalidOperation, ValueError, TypeError) as e:
            raise ValidationError(
                f"amount не может быть преобразован в число: {data['amount']} (id: {data['id']})"
            ) from e
        
        # Валидация category
        category = str(data["category"]).strip()
        if not category:
            raise ValidationError(f"category не может быть пустым (id: {data['id']})")
        
        # Валидация date
        try:
            if isinstance(data["date"], str):
                date = datetime.fromisoformat(data["date"])
            else:
                date = data["date"]
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"date неверного формата: {data['date']} (id: {data['id']})"
            ) from e
        
        return cls(
            id=str(data["id"]),
            amount=amount,
            category=category,
            date=date,
            currency=data.get("currency", "RUB"),
            raw_data=data
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Преобразует транзакцию в словарь для JSON."""
        return {
            "id": self.id,
            "amount": float(self.amount),
            "category": self.category,
            "date": self.date.isoformat(),
            "currency": self.currency
        }