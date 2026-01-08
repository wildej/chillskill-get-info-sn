"""
Модуль для работы с серийными номерами: 
- разбор пользовательского ввода
- валидация
- приведение к нормальному виду
"""

from luhn_algorithm import validate_luhn_checksum
from typing import Tuple

def parse_serial_number(user_input: str) -> Tuple[bool, str]:
    """
    Разбирает пользовательский ввод и приводит к нормальному виду.
    Проверяет что его длина равна 12, а так же что его контрольная сумма валидна.
    Форматирует серийный номер в формат XXXX-XXXX-XXXX.
    Возвращает кортеж с результатом валидации и отформатированный серийный номер.
    """
    # Извлекаем только цифры
    serial = ''.join(filter(str.isdigit, user_input))

    if len(serial) != 12:
        return False, "Серийный номер должен содержать ровно 12 цифр"
    if not validate_luhn_checksum(serial):
        return False, "Проверьте корректность введенного серийного номера, возможна опечатка"
    
    return True, f"{serial[0:4]}-{serial[4:8]}-{serial[8:12]}"