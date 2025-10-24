"""
Validators for Polish PESEL number.

PESEL (Powszechny Elektroniczny System Ewidencji Ludności) is the national
identification number used in Poland.

Format: RRMMDDPPPPK (11 digits)
- RRMMDD: Date of birth (year, month, day)
- PPPP: Serial number and gender
- K: Checksum digit

Reference: https://pl.wikipedia.org/wiki/PESEL
"""

import re
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_pesel_format(pesel):
    """
    Validate PESEL format (11 digits).

    Args:
        pesel (str): PESEL number to validate

    Raises:
        ValidationError: If PESEL format is invalid
    """
    if not pesel:
        raise ValidationError(_('PESEL jest wymagany.'))

    if not isinstance(pesel, str):
        pesel = str(pesel)

    # Remove whitespace
    pesel = pesel.strip()

    # Check length
    if len(pesel) != 11:
        raise ValidationError(_('PESEL musi składać się z 11 cyfr.'))

    # Check if all characters are digits
    if not pesel.isdigit():
        raise ValidationError(_('PESEL może zawierać tylko cyfry.'))


def validate_pesel_checksum(pesel):
    """
    Validate PESEL checksum using the official algorithm.

    The checksum is calculated as follows:
    1. Multiply each of the first 10 digits by weights: [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    2. Sum all products
    3. Take modulo 10
    4. Checksum = (10 - result) % 10
    5. Compare with the 11th digit

    Args:
        pesel (str): PESEL number to validate

    Raises:
        ValidationError: If checksum is invalid
    """
    # First validate format
    validate_pesel_format(pesel)

    if not isinstance(pesel, str):
        pesel = str(pesel)

    pesel = pesel.strip()

    # Weights for checksum calculation
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]

    # Calculate checksum
    checksum_sum = sum(int(pesel[i]) * weights[i] for i in range(10))
    checksum_calculated = (10 - (checksum_sum % 10)) % 10
    checksum_from_pesel = int(pesel[10])

    if checksum_calculated != checksum_from_pesel:
        raise ValidationError(
            _('PESEL jest nieprawidłowy. Cyfra kontrolna nie zgadza się.')
        )


def extract_birth_date_from_pesel(pesel):
    """
    Extract birth date from PESEL number.

    PESEL encodes the birth date in the first 6 digits: RRMMDD
    - For years 1900-1999: month is in range 01-12
    - For years 2000-2099: month is in range 21-32 (month + 20)
    - For years 1800-1899: month is in range 81-92 (month + 80)
    - For years 2100-2199: month is in range 41-52 (month + 40)
    - For years 2200-2299: month is in range 61-72 (month + 60)

    Args:
        pesel (str): PESEL number

    Returns:
        datetime.date or None: Birth date extracted from PESEL, or None if invalid
    """
    try:
        validate_pesel_format(pesel)

        if not isinstance(pesel, str):
            pesel = str(pesel)

        pesel = pesel.strip()

        year = int(pesel[0:2])
        month = int(pesel[2:4])
        day = int(pesel[4:6])

        # Determine century based on month encoding
        if 1 <= month <= 12:
            # 1900-1999
            year += 1900
        elif 21 <= month <= 32:
            # 2000-2099
            year += 2000
            month -= 20
        elif 81 <= month <= 92:
            # 1800-1899
            year += 1800
            month -= 80
        elif 41 <= month <= 52:
            # 2100-2199
            year += 2100
            month -= 40
        elif 61 <= month <= 72:
            # 2200-2299
            year += 2200
            month -= 60
        else:
            return None

        # Try to create a valid date
        birth_date = datetime(year, month, day).date()
        return birth_date

    except (ValueError, ValidationError):
        return None


def extract_gender_from_pesel(pesel):
    """
    Extract gender from PESEL number.

    The 10th digit (index 9) indicates gender:
    - Even number: Female
    - Odd number: Male

    Args:
        pesel (str): PESEL number

    Returns:
        str or None: 'M' for male, 'F' for female, or None if invalid
    """
    try:
        validate_pesel_format(pesel)

        if not isinstance(pesel, str):
            pesel = str(pesel)

        pesel = pesel.strip()

        gender_digit = int(pesel[9])

        if gender_digit % 2 == 0:
            return 'F'  # Female
        else:
            return 'M'  # Male

    except (ValueError, ValidationError):
        return None


def validate_pesel_birth_date_consistency(pesel, birth_date):
    """
    Validate that the birth date matches the date encoded in PESEL.

    Args:
        pesel (str): PESEL number
        birth_date (datetime.date): Birth date to compare

    Raises:
        ValidationError: If birth date doesn't match PESEL
    """
    extracted_date = extract_birth_date_from_pesel(pesel)

    if extracted_date is None:
        raise ValidationError(
            _('Nie można wyodrębnić daty urodzenia z numeru PESEL.')
        )

    if extracted_date != birth_date:
        raise ValidationError(
            _('Data urodzenia nie zgadza się z numerem PESEL. '
              f'PESEL wskazuje na datę: {extracted_date.strftime("%d.%m.%Y")}')
        )


class PESELValidator:
    """
    Django validator class for PESEL numbers.

    Usage:
        from utilities.validators import PESELValidator

        class Patient(models.Model):
            pesel = models.CharField(
                max_length=11,
                validators=[PESELValidator()]
            )
    """

    message = _('Podaj prawidłowy numer PESEL.')
    code = 'invalid_pesel'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        """
        Validate PESEL number.

        Args:
            value: PESEL number to validate

        Raises:
            ValidationError: If PESEL is invalid
        """
        try:
            validate_pesel_checksum(value)
        except ValidationError as e:
            raise ValidationError(self.message, code=self.code) from e

    def __eq__(self, other):
        return (
            isinstance(other, PESELValidator) and
            self.message == other.message and
            self.code == other.code
        )

    def deconstruct(self):
        """
        Return a 3-tuple of class import path, positional arguments,
        and keyword arguments for Django migrations.
        """
        path = 'utilities.validators.PESELValidator'
        args = []
        kwargs = {}

        # Only include non-default values
        default_message = _('Podaj prawidłowy numer PESEL.')
        if self.message != default_message:
            kwargs['message'] = self.message
        if self.code != 'invalid_pesel':
            kwargs['code'] = self.code

        return path, args, kwargs


def is_valid_pesel(pesel):
    """
    Check if PESEL is valid (convenience function).

    Args:
        pesel (str): PESEL number to validate

    Returns:
        bool: True if PESEL is valid, False otherwise
    """
    try:
        validate_pesel_checksum(pesel)
        return True
    except ValidationError:
        return False
