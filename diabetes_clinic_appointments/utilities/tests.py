"""
Tests for PESEL validators.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date
from .validators import (
    validate_pesel_format,
    validate_pesel_checksum,
    extract_birth_date_from_pesel,
    extract_gender_from_pesel,
    validate_pesel_birth_date_consistency,
    is_valid_pesel,
    PESELValidator
)


class PESELFormatValidationTest(TestCase):
    """Test PESEL format validation"""

    def test_valid_format(self):
        """Test that valid PESEL format passes"""
        valid_pesels = [
            '44051401458',
            '92032109552',
            '00210155875',
        ]
        for pesel in valid_pesels:
            try:
                validate_pesel_format(pesel)
            except ValidationError:
                self.fail(f"Valid PESEL {pesel} raised ValidationError")

    def test_invalid_length(self):
        """Test that PESEL with wrong length fails"""
        invalid_pesels = [
            '4405140145',  # 10 digits
            '440514014588',  # 12 digits
            '440',  # 3 digits
            '',  # Empty
        ]
        for pesel in invalid_pesels:
            with self.assertRaises(ValidationError):
                validate_pesel_format(pesel)

    def test_non_digits(self):
        """Test that PESEL with non-digit characters fails"""
        invalid_pesels = [
            '4405140145a',
            '44051401-58',
            '440514 1458',
            'ABCDEFGHIJK',
        ]
        for pesel in invalid_pesels:
            with self.assertRaises(ValidationError):
                validate_pesel_format(pesel)

    def test_none_value(self):
        """Test that None value fails"""
        with self.assertRaises(ValidationError):
            validate_pesel_format(None)


class PESELChecksumValidationTest(TestCase):
    """Test PESEL checksum validation"""

    def test_valid_checksums(self):
        """Test known valid PESEL numbers"""
        valid_pesels = [
            '44051401458',  # Valid PESEL (1944-05-14, Male)
            '92032109552',  # Valid PESEL (1992-03-21, Male)
            '00210155875',  # Valid PESEL (2000-01-01, Male)
            '02270803624',  # Valid PESEL (2002-07-08, Female)
            '11111111116',  # Valid checksum (edge case)
        ]
        for pesel in valid_pesels:
            try:
                validate_pesel_checksum(pesel)
            except ValidationError:
                self.fail(f"Valid PESEL {pesel} failed checksum validation")

    def test_invalid_checksums(self):
        """Test PESEL numbers with wrong checksums"""
        invalid_pesels = [
            '44051401457',  # Wrong checksum (should be 8)
            '92032109559',  # Wrong checksum (should be 2)
            '00210155874',  # Wrong checksum (should be 5)
            '11111111111',  # All ones (invalid checksum, should be 6)
            '12345678901',  # Invalid checksum
        ]
        for pesel in invalid_pesels:
            with self.assertRaises(ValidationError):
                validate_pesel_checksum(pesel)


class ExtractBirthDateTest(TestCase):
    """Test birth date extraction from PESEL"""

    def test_extract_1900s_birth_dates(self):
        """Test birth date extraction for 1900-1999"""
        test_cases = [
            ('44051401458', date(1944, 5, 14)),
            ('92032109552', date(1992, 3, 21)),
            ('56111234564', date(1956, 11, 12)),
        ]
        for pesel, expected_date in test_cases:
            extracted = extract_birth_date_from_pesel(pesel)
            self.assertEqual(extracted, expected_date,
                           f"Expected {expected_date} for PESEL {pesel}, got {extracted}")

    def test_extract_2000s_birth_dates(self):
        """Test birth date extraction for 2000-2099"""
        test_cases = [
            ('00210155875', date(2000, 1, 1)),
            ('02270803624', date(2002, 7, 8)),
            ('15322912349', date(2015, 12, 29)),
        ]
        for pesel, expected_date in test_cases:
            extracted = extract_birth_date_from_pesel(pesel)
            self.assertEqual(extracted, expected_date,
                           f"Expected {expected_date} for PESEL {pesel}, got {extracted}")

    def test_invalid_pesel_returns_none(self):
        """Test that invalid PESEL returns None"""
        invalid_pesels = [
            '12345',  # Too short
            'abcdefghijk',  # Non-digits
            '99991212345',  # Invalid month (99)
        ]
        for pesel in invalid_pesels:
            self.assertIsNone(extract_birth_date_from_pesel(pesel))


class ExtractGenderTest(TestCase):
    """Test gender extraction from PESEL"""

    def test_extract_male_gender(self):
        """Test male gender extraction (odd 10th digit)"""
        male_pesels = [
            '44051401458',  # 10th digit: 5 (odd)
            '92032109552',  # 10th digit: 5 (odd)
            '00210155875',  # 10th digit: 7 (odd)
        ]
        for pesel in male_pesels:
            gender = extract_gender_from_pesel(pesel)
            self.assertEqual(gender, 'M', f"Expected 'M' for PESEL {pesel}, got {gender}")

    def test_extract_female_gender(self):
        """Test female gender extraction (even 10th digit)"""
        female_pesels = [
            '92032109545',  # 10th digit: 4 (even)
            '44051401441',  # 10th digit: 4 (even)
        ]
        for pesel in female_pesels:
            gender = extract_gender_from_pesel(pesel)
            self.assertEqual(gender, 'F', f"Expected 'F' for PESEL {pesel}, got {gender}")

    def test_invalid_pesel_returns_none(self):
        """Test that invalid PESEL returns None"""
        invalid_pesels = [
            '12345',
            'abcdefghijk',
        ]
        for pesel in invalid_pesels:
            self.assertIsNone(extract_gender_from_pesel(pesel))


class BirthDateConsistencyTest(TestCase):
    """Test birth date consistency validation"""

    def test_matching_birth_dates(self):
        """Test that matching birth dates pass validation"""
        test_cases = [
            ('44051401458', date(1944, 5, 14)),
            ('92032109552', date(1992, 3, 21)),
            ('00210155875', date(2000, 1, 1)),
        ]
        for pesel, birth_date in test_cases:
            try:
                validate_pesel_birth_date_consistency(pesel, birth_date)
            except ValidationError:
                self.fail(f"Matching birth date for PESEL {pesel} raised ValidationError")

    def test_mismatching_birth_dates(self):
        """Test that mismatching birth dates fail validation"""
        test_cases = [
            ('44051401458', date(1944, 5, 15)),  # Wrong day
            ('92032109552', date(1992, 3, 22)),  # Wrong day
            ('00210155875', date(2000, 1, 2)),   # Wrong day
            ('44051401458', date(1945, 5, 14)),  # Wrong year
        ]
        for pesel, birth_date in test_cases:
            with self.assertRaises(ValidationError):
                validate_pesel_birth_date_consistency(pesel, birth_date)


class IsValidPESELTest(TestCase):
    """Test convenience function is_valid_pesel"""

    def test_valid_pesels_return_true(self):
        """Test that valid PESELs return True"""
        valid_pesels = [
            '44051401458',
            '92032109552',
            '00210155875',
        ]
        for pesel in valid_pesels:
            self.assertTrue(is_valid_pesel(pesel),
                          f"PESEL {pesel} should be valid")

    def test_invalid_pesels_return_false(self):
        """Test that invalid PESELs return False"""
        invalid_pesels = [
            '44051401457',  # Wrong checksum
            '12345',        # Too short
            'abcdefghijk',  # Non-digits
            '',             # Empty
        ]
        for pesel in invalid_pesels:
            self.assertFalse(is_valid_pesel(pesel),
                           f"PESEL {pesel} should be invalid")


class PESELValidatorClassTest(TestCase):
    """Test PESELValidator Django validator class"""

    def test_validator_accepts_valid_pesel(self):
        """Test that validator accepts valid PESEL"""
        validator = PESELValidator()
        valid_pesels = [
            '44051401458',
            '92032109552',
            '00210155875',
        ]
        for pesel in valid_pesels:
            try:
                validator(pesel)
            except ValidationError:
                self.fail(f"Validator rejected valid PESEL {pesel}")

    def test_validator_rejects_invalid_pesel(self):
        """Test that validator rejects invalid PESEL"""
        validator = PESELValidator()
        invalid_pesels = [
            '44051401457',  # Wrong checksum
            '12345',        # Too short
            'abcdefghijk',  # Non-digits
        ]
        for pesel in invalid_pesels:
            with self.assertRaises(ValidationError):
                validator(pesel)

    def test_custom_error_message(self):
        """Test custom error message"""
        custom_message = 'Custom PESEL error'
        validator = PESELValidator(message=custom_message)

        with self.assertRaises(ValidationError) as cm:
            validator('12345678901')  # Invalid PESEL

        self.assertEqual(str(cm.exception.messages[0]), custom_message)
