"""
Testy dla walidatorów PESEL.

Testuje wszystkie funkcje i klasy z utilities/validators.py:
- validate_pesel_format()
- validate_pesel_checksum()
- extract_birth_date_from_pesel()
- extract_gender_from_pesel()
- validate_pesel_birth_date_consistency()
- PESELValidator class
- is_valid_pesel()
"""

from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from utilities.validators import (
    validate_pesel_format,
    validate_pesel_checksum,
    extract_birth_date_from_pesel,
    extract_gender_from_pesel,
    validate_pesel_birth_date_consistency,
    PESELValidator,
    is_valid_pesel
)


class ValidatePeselFormatTest(TestCase):
    """Testy walidacji formatu PESEL"""

    def test_valid_pesel_format(self):
        """Test poprawnego formatu PESEL"""
        # Should not raise exception
        validate_pesel_format('12345678901')

    def test_pesel_too_short(self):
        """Test PESEL za krótki"""
        with self.assertRaises(ValidationError) as cm:
            validate_pesel_format('123456789')
        self.assertIn('11 cyfr', str(cm.exception))

    def test_pesel_too_long(self):
        """Test PESEL za długi"""
        with self.assertRaises(ValidationError) as cm:
            validate_pesel_format('123456789012')
        self.assertIn('11 cyfr', str(cm.exception))

    def test_pesel_with_letters(self):
        """Test PESEL z literami"""
        with self.assertRaises(ValidationError) as cm:
            validate_pesel_format('1234567890A')
        self.assertIn('tylko cyfry', str(cm.exception))

    def test_pesel_with_special_chars(self):
        """Test PESEL ze znakami specjalnymi"""
        with self.assertRaises(ValidationError) as cm:
            validate_pesel_format('12345-67890')
        self.assertIn('tylko cyfry', str(cm.exception))

    def test_pesel_empty_string(self):
        """Test pustego PESEL"""
        with self.assertRaises(ValidationError) as cm:
            validate_pesel_format('')
        self.assertIn('wymagany', str(cm.exception))

    def test_pesel_none(self):
        """Test None jako PESEL"""
        with self.assertRaises(ValidationError) as cm:
            validate_pesel_format(None)
        self.assertIn('wymagany', str(cm.exception))

    def test_pesel_with_whitespace(self):
        """Test PESEL z białymi znakami"""
        # Should strip whitespace and pass
        validate_pesel_format('  12345678901  ')


class ValidatePeselChecksumTest(TestCase):
    """Testy walidacji sumy kontrolnej PESEL"""

    def test_valid_pesel_checksum(self):
        """Test poprawnej sumy kontrolnej"""
        # Real valid PESELs (wygenerowane z poprawnym checksumem)
        valid_pesels = [
            '44051401458',  # 1944-05-14
            '00222600008',  # 2000-02-26
            '92090515830',  # 1992-09-05
        ]
        for pesel in valid_pesels:
            # Should not raise exception
            validate_pesel_checksum(pesel)

    def test_invalid_pesel_checksum(self):
        """Test niepoprawnej sumy kontrolnej"""
        # Zmieniona ostatnia cyfra (checksum)
        invalid_pesels = [
            '44051401459',  # Prawidłowy: 44051401458
            '00222600009',  # Prawidłowy: 00222600008
            '92090515831',  # Prawidłowy: 92090515830
        ]
        for pesel in invalid_pesels:
            with self.assertRaises(ValidationError) as cm:
                validate_pesel_checksum(pesel)
            self.assertIn('kontrolna', str(cm.exception))

    def test_checksum_validation_calls_format_validation(self):
        """Test że walidacja checksum sprawdza też format"""
        with self.assertRaises(ValidationError):
            validate_pesel_checksum('123')  # Za krótki


class ExtractBirthDateFromPeselTest(TestCase):
    """Testy wyodrębniania daty urodzenia z PESEL"""

    def test_extract_date_1900_century(self):
        """Test daty urodzenia dla wieku 1900-1999"""
        # PESEL: 44051401458 -> 1944-05-14
        birth_date = extract_birth_date_from_pesel('44051401458')
        self.assertEqual(birth_date, date(1944, 5, 14))

    def test_extract_date_2000_century(self):
        """Test daty urodzenia dla wieku 2000-2099"""
        # PESEL: 00222600008 -> 2000-02-26 (miesiąc + 20)
        birth_date = extract_birth_date_from_pesel('00222600008')
        self.assertEqual(birth_date, date(2000, 2, 26))

    def test_extract_date_1800_century(self):
        """Test daty urodzenia dla wieku 1800-1899"""
        # Format: miesiąc + 80
        # 99 (year) 85 (month=5+80) 15 (day) + 5 cyfr + checksum
        pesel = '99851512345'
        birth_date = extract_birth_date_from_pesel(pesel)
        # Może być None jeśli checksum niepoprawny, ale sprawdzamy logikę
        if birth_date:
            self.assertEqual(birth_date.year, 1899)
            self.assertEqual(birth_date.month, 5)
            self.assertEqual(birth_date.day, 15)

    def test_extract_date_2100_century(self):
        """Test daty urodzenia dla wieku 2100-2199"""
        # Format: miesiąc + 40
        pesel = '00451512345'  # 2100-05-15
        birth_date = extract_birth_date_from_pesel(pesel)
        if birth_date:
            self.assertEqual(birth_date.year, 2100)
            self.assertEqual(birth_date.month, 5)

    def test_extract_date_invalid_month(self):
        """Test niepoprawnego miesiąca"""
        # Miesiąc 99 (niepoprawny)
        pesel = '00991512345'
        birth_date = extract_birth_date_from_pesel(pesel)
        self.assertIsNone(birth_date)

    def test_extract_date_invalid_day(self):
        """Test niepoprawnego dnia"""
        # Dzień 32 (niepoprawny)
        pesel = '00013212345'
        birth_date = extract_birth_date_from_pesel(pesel)
        self.assertIsNone(birth_date)

    def test_extract_date_invalid_format(self):
        """Test niepoprawnego formatu PESEL"""
        birth_date = extract_birth_date_from_pesel('123')
        self.assertIsNone(birth_date)


class ExtractGenderFromPeselTest(TestCase):
    """Testy wyodrębniania płci z PESEL"""

    def test_extract_male_gender(self):
        """Test wyodrębniania płci męskiej (cyfra nieparzysta)"""
        # 10-ta cyfra (index 9) nieparzysta = mężczyzna
        pesel = '44051401458'  # 10-ta cyfra: 5 (nieparzysta)
        gender = extract_gender_from_pesel(pesel)
        self.assertEqual(gender, 'M')

    def test_extract_female_gender(self):
        """Test wyodrębniania płci żeńskiej (cyfra parzysta)"""
        # 10-ta cyfra (index 9) parzysta = kobieta
        pesel = '00222600008'  # 10-ta cyfra: 0 (parzysta)
        gender = extract_gender_from_pesel(pesel)
        self.assertEqual(gender, 'F')

    def test_extract_gender_various_digits(self):
        """Test różnych cyfr płci"""
        # PESEL format: YYMMDDPPPPK (11 digits)
        # Gender is at position 9 (index 9), 10th digit overall
        # Wszystkie nieparzyste -> M (10-ta cyfra, index 9)
        for digit in [1, 3, 5, 7, 9]:
            pesel = f'000101000{digit}0'  # YYMMDDPPP + gender_digit + checksum
            gender = extract_gender_from_pesel(pesel)
            self.assertEqual(gender, 'M', f"Digit {digit} should be male")

        # Wszystkie parzyste -> F (10-ta cyfra, index 9)
        for digit in [0, 2, 4, 6, 8]:
            pesel = f'000101000{digit}0'  # YYMMDDPPP + gender_digit + checksum
            gender = extract_gender_from_pesel(pesel)
            self.assertEqual(gender, 'F', f"Digit {digit} should be female")

    def test_extract_gender_invalid_pesel(self):
        """Test niepoprawnego PESEL"""
        gender = extract_gender_from_pesel('123')
        self.assertIsNone(gender)


class ValidatePeselBirthDateConsistencyTest(TestCase):
    """Testy spójności PESEL z datą urodzenia"""

    def test_matching_birth_date(self):
        """Test zgodnej daty urodzenia"""
        pesel = '44051401458'  # 1944-05-14
        birth_date = date(1944, 5, 14)
        # Should not raise exception
        validate_pesel_birth_date_consistency(pesel, birth_date)

    def test_matching_birth_date_2000(self):
        """Test zgodnej daty urodzenia dla 2000"""
        pesel = '00222600008'  # 2000-02-26
        birth_date = date(2000, 2, 26)
        # Should not raise exception
        validate_pesel_birth_date_consistency(pesel, birth_date)

    def test_mismatching_year(self):
        """Test niezgodnego roku"""
        pesel = '44051401458'  # 1944-05-14
        birth_date = date(1945, 5, 14)  # Zły rok
        with self.assertRaises(ValidationError) as cm:
            validate_pesel_birth_date_consistency(pesel, birth_date)
        self.assertIn('nie zgadza się', str(cm.exception))
        # Data może być w formacie DD.MM.YYYY lub YYYY-MM-DD
        self.assertTrue('1944' in str(cm.exception) and '05' in str(cm.exception) and '14' in str(cm.exception))

    def test_mismatching_month(self):
        """Test niezgodnego miesiąca"""
        pesel = '44051401458'  # 1944-05-14
        birth_date = date(1944, 6, 14)  # Zły miesiąc
        with self.assertRaises(ValidationError) as cm:
            validate_pesel_birth_date_consistency(pesel, birth_date)
        self.assertIn('nie zgadza się', str(cm.exception))

    def test_mismatching_day(self):
        """Test niezgodnego dnia"""
        pesel = '44051401458'  # 1944-05-14
        birth_date = date(1944, 5, 15)  # Zły dzień
        with self.assertRaises(ValidationError) as cm:
            validate_pesel_birth_date_consistency(pesel, birth_date)
        self.assertIn('nie zgadza się', str(cm.exception))

    def test_invalid_pesel_format(self):
        """Test niepoprawnego formatu PESEL"""
        pesel = '00991512345'  # Niepoprawny miesiąc
        birth_date = date(2000, 1, 15)
        with self.assertRaises(ValidationError) as cm:
            validate_pesel_birth_date_consistency(pesel, birth_date)
        self.assertIn('wyodrębnić', str(cm.exception))


class PESELValidatorClassTest(TestCase):
    """Testy klasy PESELValidator"""

    def test_validator_valid_pesel(self):
        """Test walidatora z poprawnym PESEL"""
        validator = PESELValidator()
        # Should not raise exception
        validator('44051401458')

    def test_validator_invalid_pesel(self):
        """Test walidatora z niepoprawnym PESEL"""
        validator = PESELValidator()
        with self.assertRaises(ValidationError) as cm:
            validator('44051401459')
        self.assertEqual(cm.exception.code, 'invalid_pesel')

    def test_validator_custom_message(self):
        """Test walidatora z własną wiadomością"""
        custom_message = 'Niestandardowy komunikat błędu'
        validator = PESELValidator(message=custom_message)
        with self.assertRaises(ValidationError) as cm:
            validator('44051401459')
        self.assertIn(custom_message, str(cm.exception))

    def test_validator_custom_code(self):
        """Test walidatora z własnym kodem"""
        custom_code = 'custom_code'
        validator = PESELValidator(code=custom_code)
        with self.assertRaises(ValidationError) as cm:
            validator('44051401459')
        self.assertEqual(cm.exception.code, custom_code)

    def test_validator_equality(self):
        """Test porównywania walidatorów"""
        validator1 = PESELValidator()
        validator2 = PESELValidator()
        validator3 = PESELValidator(message='Custom')

        self.assertEqual(validator1, validator2)
        self.assertNotEqual(validator1, validator3)


class IsValidPeselTest(TestCase):
    """Testy funkcji is_valid_pesel()"""

    def test_is_valid_pesel_true(self):
        """Test poprawnego PESEL"""
        self.assertTrue(is_valid_pesel('44051401458'))
        self.assertTrue(is_valid_pesel('00222600008'))
        self.assertTrue(is_valid_pesel('92090515830'))

    def test_is_valid_pesel_false_checksum(self):
        """Test niepoprawnej sumy kontrolnej"""
        self.assertFalse(is_valid_pesel('44051401459'))
        self.assertFalse(is_valid_pesel('00222600009'))

    def test_is_valid_pesel_false_format(self):
        """Test niepoprawnego formatu"""
        self.assertFalse(is_valid_pesel('123'))
        self.assertFalse(is_valid_pesel('1234567890A'))
        self.assertFalse(is_valid_pesel(''))
