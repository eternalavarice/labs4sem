"""Кастомные исключения для проекта."""


class BaseAppError(Exception):
    """Базовое исключение для всех ошибок приложения."""
    pass


class FatalError(BaseAppError):
    """Фатальная ошибка - программа не может продолжать работу."""
    pass


class DataFormatError(BaseAppError):
    """Ошибка структуры файла (неверный формат, отсутствуют колонки)."""
    pass


class ValidationError(BaseAppError):
    """Ошибка бизнес-логики (некорректные данные в записи)."""
    pass


class CurrencyMismatchError(ValidationError):
    """Ошибка несоответствия валют в отчетах."""
    pass


class DuplicateIdError(ValidationError):
    """Ошибка дублирования ID транзакции."""
    pass