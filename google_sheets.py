"""
Модуль для работы с Google Sheets: получение данных по серийному номеру.
"""
import os
import json
from typing import Optional, Dict, List
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

# Загружаем переменные окружения
load_dotenv()

# Настройки из переменных окружения
SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME", "Sheet1")
SHEET_PAT = os.getenv("SHEET_PAT")  # Путь к JSON файлу service account или сам JSON
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # Альтернативный способ
SERIAL_NUMBER_COLUMN = int(os.getenv("SERIAL_NUMBER_COLUMN", "1"))  # Номер столбца с серийными номерами (1-based)
IGNORE_COLUMNS = os.getenv("IGNORE_COLUMNS", "")  # Номера столбцов через запятую, которые нужно игнорировать

# Парсим игнорируемые столбцы
_ignore_columns_set = set()
if IGNORE_COLUMNS:
    _ignore_columns_set = {int(col.strip()) for col in IGNORE_COLUMNS.split(",") if col.strip()}


def _get_credentials():
    """
    Получает credentials для доступа к Google Sheets.
    Поддерживает несколько способов:
    1. SHEET_PAT как путь к JSON файлу
    2. SHEET_PAT как сам JSON содержимое
    3. GOOGLE_APPLICATION_CREDENTIALS как путь к JSON файлу
    """
    credentials = None
    
    # Способ 1: SHEET_PAT как путь к файлу или сам JSON
    if SHEET_PAT:
        if os.path.exists(SHEET_PAT):
            # Это путь к файлу
            credentials = Credentials.from_service_account_file(
                SHEET_PAT,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
        else:
            # Попробуем как JSON строку
            try:
                creds_dict = json.loads(SHEET_PAT)
                credentials = Credentials.from_service_account_info(
                    creds_dict,
                    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
                )
            except json.JSONDecodeError:
                raise ValueError("SHEET_PAT должен быть либо путем к JSON файлу, либо валидным JSON")
    
    # Способ 2: GOOGLE_APPLICATION_CREDENTIALS
    elif GOOGLE_APPLICATION_CREDENTIALS:
        if os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
            credentials = Credentials.from_service_account_file(
                GOOGLE_APPLICATION_CREDENTIALS,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
        else:
            raise ValueError(f"GOOGLE_APPLICATION_CREDENTIALS указывает на несуществующий файл: {GOOGLE_APPLICATION_CREDENTIALS}")
    
    if not credentials:
        raise ValueError(
            "Необходимо указать либо SHEET_PAT (путь к JSON файлу service account или сам JSON), "
            "либо GOOGLE_APPLICATION_CREDENTIALS (путь к JSON файлу)"
        )
    
    return credentials


def _get_sheet():
    """
    Получает объект листа Google Sheets.
    """
    if not SHEET_ID:
        raise ValueError("SHEET_ID не установлен в переменных окружения!")
    
    credentials = _get_credentials()
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SHEET_ID)
    worksheet = spreadsheet.worksheet(SHEET_NAME)
    return worksheet


def get_data_by_serial_number(serial_number: str) -> Optional[Dict[str, str]]:
    """
    Получает данные из Google Sheets по серийному номеру.
    
    Args:
        serial_number: Серийный номер для поиска (уже валидированный и нормализованный)
    
    Returns:
        Словарь с данными, где ключи - заголовки столбцов, значения - данные из строки.
        Если серийный номер не найден, возвращает None.
    """
    try:
        worksheet = _get_sheet()
        
        # Получаем все данные из листа
        all_values = worksheet.get_all_values()
        
        if not all_values:
            return None
        
        # Первая строка - заголовки
        headers = all_values[0]
        
        # Определяем индекс столбца с серийными номерами (переводим из 1-based в 0-based)
        serial_col_index = SERIAL_NUMBER_COLUMN - 1
        
        if serial_col_index < 0 or serial_col_index >= len(headers):
            raise ValueError(f"Столбец {SERIAL_NUMBER_COLUMN} выходит за пределы таблицы")
        
        # Ищем строку с нужным серийным номером
        # Нормализуем серийный номер для поиска (убираем дефисы, пробелы)
        normalized_serial = ''.join(filter(str.isdigit, serial_number))
        
        found_row = None
        for row_index, row in enumerate(all_values[1:], start=1):  # Пропускаем заголовок
            if len(row) > serial_col_index:
                # Нормализуем серийный номер из таблицы для сравнения
                cell_value = str(row[serial_col_index]).strip()
                normalized_cell = ''.join(filter(str.isdigit, cell_value))
                
                if normalized_cell == normalized_serial:
                    found_row = row
                    break
        
        if not found_row:
            return None
        
        # Формируем словарь с данными
        result = {}
        for col_index, header in enumerate(headers):
            # Пропускаем игнорируемые столбцы и столбец с серийным номером
            col_number = col_index + 1  # 1-based номер столбца
            if col_number in _ignore_columns_set or col_index == serial_col_index:
                continue
            
            # Получаем значение из найденной строки
            value = found_row[col_index] if col_index < len(found_row) else ""
            result[header] = value.strip() if value else ""
        
        return result
        
    except Exception as e:
        raise Exception(f"Ошибка при получении данных из Google Sheets: {str(e)}")


def format_data_for_display(data: Dict[str, str]) -> str:
    """
    Форматирует данные для отображения пользователю.
    
    Args:
        data: Словарь с данными (заголовок -> значение)
    
    Returns:
        Отформатированная строка для вывода
    """
    if not data:
        return "Данные не найдены"
    
    lines = []
    for header, value in data.items():
        if value:  # Показываем только непустые значения
            lines.append(f"**{header}**\n{value}")
    
    return "\n\n".join(lines) if lines else "Данные не найдены"
