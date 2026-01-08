"""
Тесты для модуля алгоритма Луна и работы с серийными номерами.
"""
import pytest
from luhn_algorithm import validate_luhn_checksum, add_valid_luhn_checksum
from serial_number import parse_serial_number


class TestValidateLuhnChecksum:
    """Тесты для метода validate_luhn_checksum."""
    
    def test_valid_visa_card(self):
        """Тест валидного номера Visa карты."""
        assert validate_luhn_checksum('4532549385285775') == True
        assert validate_luhn_checksum('4539148803436467') == True
    
    def test_valid_mastercard(self):
        """Тест валидного номера MasterCard."""
        assert validate_luhn_checksum('5424564177250828') == True
    
    def test_valid_american_express(self):
        """Тест валидного номера American Express."""
        assert validate_luhn_checksum('375909374676368') == True
    
    def test_valid_discover(self):
        """Тест валидного номера Discover."""
        assert validate_luhn_checksum('6011977278646461') == True
    
    def test_valid_jcb(self):
        """Тест валидного номера JCB."""
        assert validate_luhn_checksum('3528192949271243') == True
    
    def test_valid_diners_club(self):
        """Тест валидного номера Diners Club."""
        assert validate_luhn_checksum('30008036405527') == True
    
    def test_valid_maestro(self):
        """Тест валидного номера Maestro."""
        assert validate_luhn_checksum('5018427297290169') == True
    
    def test_valid_imei(self):
        """Тест валидного IMEI номера."""
        assert validate_luhn_checksum('490154203237518') == True
    
    def test_valid_known_test_number(self):
        """Тест известного тестового номера."""
        assert validate_luhn_checksum('79927398713') == True
    
    def test_invalid_numbers(self):
        """Тест невалидных номеров (с измененной последней цифрой)."""
        invalid_numbers = [
            '4532549385285774',  # Visa с измененной последней цифрой
            '5424564177250829',  # MasterCard с измененной последней цифрой
            '375909374676369',   # American Express с измененной последней цифрой
            '6011977278646462',  # Discover с измененной последней цифрой
            '3528192949271244',  # JCB с измененной последней цифрой
            '30008036405528',    # Diners Club с измененной последней цифрой
            '5018427297290168',  # Maestro с измененной последней цифрой
            '79927398712',       # Известный тестовый номер с измененной последней цифрой
        ]
        for number in invalid_numbers:
            assert validate_luhn_checksum(number) == False
    
    def test_empty_string(self):
        """Тест пустой строки."""
        assert validate_luhn_checksum('') == True  # Пустая строка дает checksum = 0


class TestAddValidLuhnChecksum:
    """Тесты для метода add_valid_luhn_checksum."""
    
    def test_visa_card(self):
        """Тест добавления контрольной цифры для Visa."""
        partial = '453254938528577'
        expected = '4532549385285775'
        result = add_valid_luhn_checksum(partial)
        assert result == expected
        assert validate_luhn_checksum(result) == True
    
    def test_mastercard(self):
        """Тест добавления контрольной цифры для MasterCard."""
        partial = '542456417725082'
        expected = '5424564177250828'
        result = add_valid_luhn_checksum(partial)
        assert result == expected
        assert validate_luhn_checksum(result) == True
    
    def test_american_express(self):
        """Тест добавления контрольной цифры для American Express."""
        partial = '37590937467636'
        expected = '375909374676368'
        result = add_valid_luhn_checksum(partial)
        assert result == expected
        assert validate_luhn_checksum(result) == True
    
    def test_discover(self):
        """Тест добавления контрольной цифры для Discover."""
        partial = '601197727864646'
        expected = '6011977278646461'
        result = add_valid_luhn_checksum(partial)
        assert result == expected
        assert validate_luhn_checksum(result) == True
    
    def test_jcb(self):
        """Тест добавления контрольной цифры для JCB."""
        partial = '352819294927124'
        expected = '3528192949271243'
        result = add_valid_luhn_checksum(partial)
        assert result == expected
        assert validate_luhn_checksum(result) == True
    
    def test_diners_club(self):
        """Тест добавления контрольной цифры для Diners Club."""
        partial = '3000803640552'
        expected = '30008036405527'
        result = add_valid_luhn_checksum(partial)
        assert result == expected
        assert validate_luhn_checksum(result) == True
    
    def test_maestro(self):
        """Тест добавления контрольной цифры для Maestro."""
        partial = '501842729729016'
        expected = '5018427297290169'
        result = add_valid_luhn_checksum(partial)
        assert result == expected
        assert validate_luhn_checksum(result) == True
    
    def test_known_test_number(self):
        """Тест известного тестового номера."""
        partial = '7992739871'
        expected = '79927398713'
        result = add_valid_luhn_checksum(partial)
        assert result == expected
        assert validate_luhn_checksum(result) == True
    
    def test_multiple_cards(self):
        """Тест нескольких карт одновременно."""
        test_cases = [
            ('453254938528577', '4532549385285775'),
            ('542456417725082', '5424564177250828'),
            ('37590937467636', '375909374676368'),
            ('601197727864646', '6011977278646461'),
            ('352819294927124', '3528192949271243'),
            ('3000803640552', '30008036405527'),
            ('501842729729016', '5018427297290169'),
        ]
        for partial, expected in test_cases:
            result = add_valid_luhn_checksum(partial)
            assert result == expected
            assert validate_luhn_checksum(result) == True
    
    def test_generated_number_is_valid(self):
        """Тест что сгенерированный номер всегда валиден."""
        test_numbers = [
            '1234567890',
            '9876543210',
            '1111111111',
            '9999999999',
            '453914880343646',
        ]
        for number in test_numbers:
            result = add_valid_luhn_checksum(number)
            assert validate_luhn_checksum(result) == True


class TestParseSerialNumber:
    """Тесты для метода parse_serial_number."""
    
    def test_valid_serial_number_without_formatting(self):
        """Тест валидного серийного номера без форматирования."""
        # Генерируем валидный 12-значный номер
        valid_serial = add_valid_luhn_checksum('12345678901')
        is_valid, result = parse_serial_number(valid_serial)
        assert is_valid == True
        assert result == f"{valid_serial[0:4]}-{valid_serial[4:8]}-{valid_serial[8:12]}"
    
    def test_valid_serial_number_with_dashes(self):
        """Тест валидного серийного номера с дефисами."""
        # Генерируем валидный 12-значный номер
        valid_serial = add_valid_luhn_checksum('98765432109')
        is_valid, result = parse_serial_number(f"{valid_serial[0:4]}-{valid_serial[4:8]}-{valid_serial[8:12]}")
        assert is_valid == True
        assert result == f"{valid_serial[0:4]}-{valid_serial[4:8]}-{valid_serial[8:12]}"
    
    def test_valid_serial_number_with_spaces(self):
        """Тест валидного серийного номера с пробелами."""
        # Генерируем валидный 12-значный номер
        valid_serial = add_valid_luhn_checksum('11111111111')
        is_valid, result = parse_serial_number(f"{valid_serial[0:4]} {valid_serial[4:8]} {valid_serial[8:12]}")
        assert is_valid == True
        assert result == f"{valid_serial[0:4]}-{valid_serial[4:8]}-{valid_serial[8:12]}"
    
    def test_valid_serial_number_with_mixed_formatting(self):
        """Тест валидного серийного номера со смешанным форматированием."""
        # Генерируем валидный 12-значный номер
        valid_serial = add_valid_luhn_checksum('55555555555')
        is_valid, result = parse_serial_number(f"  {valid_serial[0:4]}-{valid_serial[4:8]} {valid_serial[8:12]}  ")
        assert is_valid == True
        assert result == f"{valid_serial[0:4]}-{valid_serial[4:8]}-{valid_serial[8:12]}"
    
    def test_invalid_length_too_short(self):
        """Тест серийного номера с недостаточной длиной."""
        is_valid, result = parse_serial_number('12345678901')
        assert is_valid == False
        assert result == "Серийный номер должен содержать ровно 12 цифр"
    
    def test_invalid_length_too_long(self):
        """Тест серийного номера с избыточной длиной."""
        is_valid, result = parse_serial_number('1234567890123')
        assert is_valid == False
        assert result == "Серийный номер должен содержать ровно 12 цифр"
    
    def test_invalid_length_empty(self):
        """Тест пустого серийного номера."""
        is_valid, result = parse_serial_number('')
        assert is_valid == False
        assert result == "Серийный номер должен содержать ровно 12 цифр"
    
    def test_invalid_length_only_spaces(self):
        """Тест серийного номера только с пробелами."""
        is_valid, result = parse_serial_number('   ')
        assert is_valid == False
        assert result == "Серийный номер должен содержать ровно 12 цифр"
    
    def test_invalid_luhn_checksum(self):
        """Тест серийного номера с невалидной контрольной суммой."""
        # Берем валидный номер и меняем последнюю цифру
        valid_serial = add_valid_luhn_checksum('12345678901')
        invalid_serial = valid_serial[:-1] + str((int(valid_serial[-1]) + 1) % 10)
        is_valid, result = parse_serial_number(invalid_serial)
        assert is_valid == False
        assert result == "Проверьте корректность введенного серийного номера, возможна опечатка"
    
    def test_invalid_luhn_checksum_with_formatting(self):
        """Тест серийного номера с невалидной контрольной суммой и форматированием."""
        # Берем валидный номер и меняем последнюю цифру
        valid_serial = add_valid_luhn_checksum('99999999999')
        invalid_serial = valid_serial[:-1] + str((int(valid_serial[-1]) + 1) % 10)
        formatted_invalid = f"{invalid_serial[0:4]}-{invalid_serial[4:8]}-{invalid_serial[8:12]}"
        is_valid, result = parse_serial_number(formatted_invalid)
        assert is_valid == False
        assert result == "Проверьте корректность введенного серийного номера, возможна опечатка"
    
    def test_serial_number_with_non_digit_characters(self):
        """Тест серийного номера с нецифровыми символами."""
        # Генерируем валидный 12-значный номер
        valid_serial = add_valid_luhn_checksum('12345678901')
        is_valid, result = parse_serial_number(f"SN{valid_serial}ABC")
        assert is_valid == True
        assert result == f"{valid_serial[0:4]}-{valid_serial[4:8]}-{valid_serial[8:12]}"
    
    def test_multiple_valid_serials(self):
        """Тест нескольких валидных серийных номеров."""
        test_cases = [
            '12345678901',
            '98765432109',
            '11111111111',
            '55555555555',
            '99999999999',
        ]
        for partial in test_cases:
            valid_serial = add_valid_luhn_checksum(partial)
            is_valid, result = parse_serial_number(valid_serial)
            assert is_valid == True
            assert result == f"{valid_serial[0:4]}-{valid_serial[4:8]}-{valid_serial[8:12]}"
    
    def test_serial_number_formatting_output(self):
        """Тест правильности форматирования вывода."""
        # Генерируем валидный 12-значный номер
        valid_serial = add_valid_luhn_checksum('12345678901')
        is_valid, result = parse_serial_number(valid_serial)
        assert is_valid == True
        # Проверяем формат XXXX-XXXX-XXXX
        parts = result.split('-')
        assert len(parts) == 3
        assert len(parts[0]) == 4
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert result == f"{valid_serial[0:4]}-{valid_serial[4:8]}-{valid_serial[8:12]}"
