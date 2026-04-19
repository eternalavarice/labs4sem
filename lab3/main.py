#!/usr/bin/env python3
"""Точка входа в приложение Data Integration Engine."""

import sys
import logging
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import NoReturn

from app.core.exceptions import FatalError
from app.services.processor import DataProcessor


def setup_logging(log_file: Path = Path("app.log")) -> None:
    """
    Настраивает логирование.
    
    Args:
        log_file: Путь к файлу логов
    """
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настройка файлового обработчика
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Настройка консольного обработчика
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def export_result_with_transactionality(
    data: dict, 
    output_path: Path,
    temp_suffix: str = ".tmp"
) -> bool:
    """
    Экспортирует результат с транзакционной записью.
    
    Сначала записывает во временный файл, затем переименовывает.
    Это гарантирует, что при сбое во время записи не повредится существующий файл.
    
    Args:
        data: Данные для экспорта
        output_path: Конечный путь к файлу
        temp_suffix: Суффикс временного файла
        
    Returns:
        bool: True если успешно, False если ошибка
    """
    temp_path = output_path.with_suffix(output_path.suffix + temp_suffix)
    
    try:
        # Записываем во временный файл
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()  # Явно сбрасываем буфер ПЕРЕД закрытием файла
        
        # Атомарно заменяем файл (если целевой файл существует, он будет перезаписан)
        # Используем replace вместо move для лучшей атомарности на разных ОС
        if temp_path.exists():
            shutil.move(str(temp_path), str(output_path))
        
        return True
        
    except (OSError, IOError) as e:
        logging.error(f"Ошибка при записи результата: {e}")
        # Пытаемся удалить временный файл, если он остался
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        return False


def generate_sample_data(data_dir: Path) -> None:
    """
    Генерирует примеры тестовых данных для демонстрации.
    
    Args:
        data_dir: Директория для сохранения тестовых данных
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Хороший CSV файл
    good_csv = data_dir / "good_transactions.csv"
    good_csv.write_text(
        "id,amount,category,date,currency\n"
        "1,100.50,Food,2024-01-15,RUB\n"
        "2,250.00,Transport,2024-01-16,RUB\n"
        "3,75.30,Entertainment,2024-01-17,RUB\n"
        "4,500.00,Shopping,2024-01-18,RUB\n",
        encoding='utf-8'
    )
    
    # Хороший JSON файл
    good_json = data_dir / "good_transactions.json"
    good_json.write_text(
        '[\n'
        '  {"id": "5", "amount": 1200.00, "category": "Rent", "date": "2024-01-01", "currency": "RUB"},\n'
        '  {"id": "6", "amount": 350.50, "category": "Utilities", "date": "2024-01-02", "currency": "RUB"},\n'
        '  {"id": "7", "amount": 89.99, "category": "Food", "date": "2024-01-03", "currency": "RUB"}\n'
        ']',
        encoding='utf-8'
    )
    
    # Файл с ошибками (отрицательная сумма)
    bad_amount = data_dir / "bad_amount.csv"
    bad_amount.write_text(
        "id,amount,category,date\n"
        "8,100.00,Food,2024-01-15\n"
        "9,-50.00,Transport,2024-01-16\n"
        "10,75.00,Entertainment,2024-01-17\n",
        encoding='utf-8'
    )
    
    # Файл с отсутствующими полями
    missing_fields = data_dir / "missing_fields.json"
    missing_fields.write_text(
        '[\n'
        '  {"id": "11", "amount": 200, "date": "2024-01-15"},\n'
        '  {"id": "12", "amount": 300, "category": "Food", "date": "2024-01-16"}\n'
        ']',
        encoding='utf-8'
    )
    
    # Пустой файл
    empty_file = data_dir / "empty.csv"
    empty_file.write_text("", encoding='utf-8')
    
    # Файл с дубликатами ID
    duplicates = data_dir / "duplicates.csv"
    duplicates.write_text(
        "id,amount,category,date\n"
        "13,100,Food,2024-01-15\n"
        "13,200,Transport,2024-01-16\n",
        encoding='utf-8'
    )
    
    # Файл с неверным форматом даты
    bad_date = data_dir / "bad_date.json"
    bad_date.write_text(
        '[\n'
        '  {"id": "14", "amount": 100, "category": "Food", "date": "not-a-date"}\n'
        ']',
        encoding='utf-8'
    )
    
    # Файл с неверным JSON
    bad_json = data_dir / "invalid.json"
    bad_json.write_text(
        '{ this is not valid json ',
        encoding='utf-8'
    )
    
    # Дополнительный файл с корректными данными в другом формате
    another_good_csv = data_dir / "another_transactions.csv"
    another_good_csv.write_text(
        "id;amount;category;date;currency\n"
        "15;45.50;Coffee;2024-01-20;RUB\n"
        "16;120.00;Books;2024-01-21;RUB\n",
        encoding='utf-8'
    )
    
    print(f"Сгенерированы тестовые данные в {data_dir}")
    print("  - good_transactions.csv (4 записи)")
    print("  - good_transactions.json (3 записи)")
    print("  - another_transactions.csv (2 записи)")
    print("  - bad_amount.csv (1 ошибочная запись)")
    print("  - bad_date.json (1 ошибочная запись)")
    print("  - duplicates.csv (1 дубликат)")
    print("  - missing_fields.json (1 ошибочная запись)")
    print("  - empty.csv (пустой файл)")
    print("  - invalid.json (битый JSON)")


def main(data_dir: str = "data", output_file: str = "result.json") -> int:
    """
    Основная функция приложения.
    
    Args:
        data_dir: Путь к директории с входными файлами
        output_file: Путь к выходному JSON файлу
        
    Returns:
        int: Код возврата (0 - успех, 1 - ошибка)
    """
    # Настраиваем логирование
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Запуск Data Integration Engine")
    logger.info(f"Входная директория: {data_dir}")
    logger.info(f"Выходной файл: {output_file}")
    
    try:
        data_path = Path(data_dir)
        
        # Если директория пуста или не существует, генерируем примеры
        if not data_path.exists():
            logger.warning("Директория с данными не существует. Генерируем примеры...")
            generate_sample_data(data_path)
        elif not any(data_path.iterdir()):
            logger.warning("Директория с данными пуста. Генерируем примеры...")
            generate_sample_data(data_path)
        
        # Создаем процессор и обрабатываем данные
        processor = DataProcessor()
        processor.process_directory(data_path)
        
        # Получаем отчет
        report = processor.get_report()
        
        # Экспортируем результат с транзакционной записью
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if export_result_with_transactionality(report["aggregated_data"], output_path):
            logger.info(f"Результат успешно сохранен в {output_path}")
        else:
            logger.error("Не удалось сохранить результат")
            return 1
        
        # Выводим красивый отчет в консоль
        print("\n" + "=" * 60)
        print("ОТЧЕТ ОБ ОБРАБОТКЕ")
        print("=" * 60)
        print(f"Обработано файлов: {report['summary']['processed_files']}")
        print(f"Пропущено файлов: {report['summary']['skipped_files']}")
        print(f"Всего транзакций: {report['summary']['total_transactions']}")
        print(f"Всего ошибок: {report['summary']['total_errors']}")
        
        if report['summary']['total_errors'] > 0:
            print("\nПервые 5 ошибок:")
            for err in report['errors'][:5]:
                error_msg = err['message'][:100]
                print(f"   - {err['file']}: {err['error_type']}")
                print(f"     {error_msg}...")
        
        print("\nАгрегированные данные по категориям:")
        if report['aggregated_data']['categories']:
            for category, amount in sorted(report['aggregated_data']['categories'].items()):
                print(f"   {category}: {amount:.2f} RUB")
        else:
            print("   (нет данных)")
        
        print(f"\nОбщая сумма: {report['aggregated_data']['total_amount']:.2f} RUB")
        print(f"Количество транзакций: {report['aggregated_data']['transaction_count']}")
        
        # Вывод списка успешно обработанных файлов
        if report['processed_files_list']:
            print(f"\nУспешно обработаны:")
            for f in report['processed_files_list']:
                print(f"   - {Path(f).name}")
        
        # Вывод списка пропущенных файлов
        if report['skipped_files_list']:
            print(f"\nПропущены/с ошибками:")
            for f in report['skipped_files_list']:
                print(f"   - {Path(f).name}")
        
        print("\n" + "=" * 60)
        print(f"Подробный лог сохранен в app.log")
        print(f"Результат сохранен в {output_file}")
        
        return 0
        
    except FatalError as e:
        logger.critical(f"Фатальная ошибка: {e}")
        print(f"\nФатальная ошибка: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        logger.info("Программа прервана пользователем")
        print("\nПрограмма прервана", file=sys.stderr)
        return 130
    except Exception as e:
        logger.exception(f"Необработанная ошибка: {e}")
        print(f"\nНеобработанная ошибка: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # Парсинг аргументов командной строки
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Data Integration Engine - обработка финансовых отчетов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py                      # Обработка данных из папки data/
  python main.py --data-dir ./my_data # Обработка из папки my_data/
  python main.py -d ./data -o out.json # Указать вход и выход
        """
    )
    parser.add_argument(
        "--data-dir", "-d",
        default="data",
        help="Директория с входными файлами (по умолчанию: data)"
    )
    parser.add_argument(
        "--output", "-o",
        default="result.json",
        help="Выходной JSON файл (по умолчанию: result.json)"
    )
    
    args = parser.parse_args()
    sys.exit(main(args.data_dir, args.output))