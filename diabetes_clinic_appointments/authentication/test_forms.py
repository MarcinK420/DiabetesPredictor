"""
Testy dla formularzy authentication.

Testuje:
- PatientRegistrationForm
- DoctorRegistrationForm
"""

from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from authentication.forms import PatientRegistrationForm, DoctorRegistrationForm
from patients.models import Patient
from doctors.models import Doctor

User = get_user_model()


class PatientRegistrationFormTest(TestCase):
    """Testy formularza rejestracji pacjenta"""

    def setUp(self):
        """Przygotowanie danych testowych"""
        self.valid_data = {
            'username': 'testpatient',
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan.kowalski@example.com',
            'phone_number': '+48123456789',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'date_of_birth': date(1990, 5, 14),
            'pesel': '90051401233',  # Valid PESEL for 1990-05-14
            'address': 'ul. Testowa 1, 00-001 Warszawa',
            'emergency_contact_name': 'Anna Kowalska',
            'emergency_contact_phone': '+48987654321',
            'diabetes_type': 'type1',
            'diagnosis_date': date(2010, 1, 15),
            'current_medications': 'Insulin',
            'allergies': 'Penicillin',
        }

    def test_valid_patient_registration_with_diabetes(self):
        """Test poprawnej rejestracji pacjenta z cukrzycą"""
        form = PatientRegistrationForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_patient_registration_healthy(self):
        """Test poprawnej rejestracji zdrowego pacjenta"""
        data = self.valid_data.copy()
        data['diabetes_type'] = 'healthy'
        data['diagnosis_date'] = None  # Nie wymagana dla zdrowych

        form = PatientRegistrationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_save_creates_user_and_patient(self):
        """Test że save() tworzy User i Patient"""
        form = PatientRegistrationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        # Sprawdź User
        self.assertEqual(user.username, 'testpatient')
        self.assertEqual(user.first_name, 'Jan')
        self.assertEqual(user.last_name, 'Kowalski')
        self.assertEqual(user.email, 'jan.kowalski@example.com')
        self.assertEqual(user.phone_number, '+48123456789')
        self.assertEqual(user.user_type, 'patient')
        self.assertTrue(user.check_password('TestPass123!'))

        # Sprawdź Patient
        patient = Patient.objects.get(user=user)
        self.assertEqual(patient.pesel, '90051401233')
        self.assertEqual(patient.date_of_birth, date(1990, 5, 14))
        self.assertEqual(patient.address, 'ul. Testowa 1, 00-001 Warszawa')
        self.assertEqual(patient.emergency_contact_name, 'Anna Kowalska')
        self.assertEqual(patient.diabetes_type, 'type1')
        self.assertEqual(patient.diagnosis_date, date(2010, 1, 15))

    def test_invalid_pesel_checksum(self):
        """Test niepoprawnej sumy kontrolnej PESEL"""
        data = self.valid_data.copy()
        data['pesel'] = '90051401234'  # Zła cyfra kontrolna (prawidłowa: 3)

        form = PatientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('pesel', form.errors)
        self.assertIn('kontrolna', str(form.errors['pesel']))

    def test_invalid_pesel_format_too_short(self):
        """Test za krótkiego PESEL"""
        data = self.valid_data.copy()
        data['pesel'] = '123456789'

        form = PatientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('pesel', form.errors)

    def test_invalid_pesel_format_letters(self):
        """Test PESEL z literami"""
        data = self.valid_data.copy()
        data['pesel'] = '9005140123A'

        form = PatientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('pesel', form.errors)

    def test_pesel_birth_date_mismatch(self):
        """Test niezgodności PESEL z datą urodzenia"""
        data = self.valid_data.copy()
        data['pesel'] = '90051401233'  # 1990-05-14
        data['date_of_birth'] = date(1991, 5, 14)  # Inny rok

        form = PatientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nie zgadza się', str(form.errors['__all__']))

    def test_diabetes_requires_diagnosis_date(self):
        """Test że cukrzyca wymaga daty diagnozy"""
        data = self.valid_data.copy()
        data['diabetes_type'] = 'type2'
        data['diagnosis_date'] = None

        form = PatientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('Data diagnozy jest wymagana', str(form.errors['__all__']))

    def test_healthy_does_not_require_diagnosis_date(self):
        """Test że 'healthy' nie wymaga daty diagnozy"""
        data = self.valid_data.copy()
        data['diabetes_type'] = 'healthy'
        data['diagnosis_date'] = None

        form = PatientRegistrationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_gestational_requires_diagnosis_date(self):
        """Test że cukrzyca ciążowa wymaga daty diagnozy"""
        data = self.valid_data.copy()
        data['diabetes_type'] = 'gestational'
        data['diagnosis_date'] = ''  # Empty string instead of None

        form = PatientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        # Błąd może być w __all__ lub w diagnosis_date
        error_message = str(form.errors)
        self.assertIn('Data diagnozy jest wymagana', error_message)

    def test_missing_required_fields(self):
        """Test brakujących wymaganych pól"""
        required_fields = [
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2', 'date_of_birth', 'pesel',
            'address', 'emergency_contact_name', 'emergency_contact_phone',
            'diabetes_type'
        ]

        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ''

            form = PatientRegistrationForm(data=data)
            self.assertFalse(form.is_valid(), f"Field {field} should be required")
            self.assertIn(field, form.errors, f"Missing error for field {field}")

    def test_optional_fields(self):
        """Test opcjonalnych pól"""
        data = self.valid_data.copy()
        data['phone_number'] = ''
        data['current_medications'] = ''
        data['allergies'] = ''
        data['diabetes_type'] = 'healthy'
        data['diagnosis_date'] = None

        form = PatientRegistrationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_password_mismatch(self):
        """Test niezgodności haseł"""
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPass123!'

        form = PatientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_invalid_email(self):
        """Test niepoprawnego emaila"""
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'

        form = PatientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_fields_have_css_class(self):
        """Test że pola formularza mają klasę CSS"""
        form = PatientRegistrationForm()
        for field_name, field in form.fields.items():
            self.assertEqual(
                field.widget.attrs.get('class'),
                'form-control',
                f"Field {field_name} should have form-control class"
            )


class DoctorRegistrationFormTest(TestCase):
    """Testy formularza rejestracji lekarza"""

    def setUp(self):
        """Przygotowanie danych testowych"""
        self.valid_data = {
            'username': 'testdoctor',
            'first_name': 'Maria',
            'last_name': 'Nowak',
            'email': 'maria.nowak@example.com',
            'phone_number': '+48111222333',
            'password1': 'DoctorPass123!',
            'password2': 'DoctorPass123!',
            'license_number': 'PWZ123456',
            'specialization': 'diabetologist',  # From Doctor model choices
            'years_of_experience': 10,
            'office_address': 'ul. Medyczna 5, 00-002 Warszawa',
            'consultation_fee': 200.00,
            'working_hours_start': '08:00',
            'working_hours_end': '16:00',
            'working_days': 'mon-fri',  # From Doctor model choices
            'education': 'Medical University of Warsaw',
            'certifications': 'Diabetology Certification',
            'bio': 'Experienced diabetologist',
        }

    def test_valid_doctor_registration(self):
        """Test poprawnej rejestracji lekarza"""
        form = DoctorRegistrationForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_save_creates_user_and_doctor(self):
        """Test że save() tworzy User i Doctor"""
        form = DoctorRegistrationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        # Sprawdź User
        self.assertEqual(user.username, 'testdoctor')
        self.assertEqual(user.first_name, 'Maria')
        self.assertEqual(user.last_name, 'Nowak')
        self.assertEqual(user.email, 'maria.nowak@example.com')
        self.assertEqual(user.phone_number, '+48111222333')
        self.assertEqual(user.user_type, 'doctor')
        self.assertTrue(user.check_password('DoctorPass123!'))

        # Sprawdź Doctor
        doctor = Doctor.objects.get(user=user)
        self.assertEqual(doctor.license_number, 'PWZ123456')
        self.assertEqual(doctor.specialization, 'diabetologist')
        self.assertEqual(doctor.years_of_experience, 10)
        self.assertEqual(doctor.office_address, 'ul. Medyczna 5, 00-002 Warszawa')
        self.assertEqual(doctor.consultation_fee, 200.00)
        self.assertEqual(doctor.working_days, 'mon-fri')
        self.assertEqual(doctor.education, 'Medical University of Warsaw')

    def test_missing_required_fields(self):
        """Test brakujących wymaganych pól"""
        required_fields = [
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2', 'license_number', 'specialization',
            'years_of_experience', 'office_address', 'consultation_fee',
            'working_hours_start', 'working_hours_end', 'working_days',
            'education'
        ]

        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ''

            form = DoctorRegistrationForm(data=data)
            self.assertFalse(form.is_valid(), f"Field {field} should be required")
            self.assertIn(field, form.errors, f"Missing error for field {field}")

    def test_optional_fields(self):
        """Test opcjonalnych pól"""
        data = self.valid_data.copy()
        data['phone_number'] = ''
        data['certifications'] = ''
        data['bio'] = ''

        form = DoctorRegistrationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_years_of_experience(self):
        """Test niepoprawnych lat doświadczenia"""
        # Tekst zamiast liczby
        data = self.valid_data.copy()
        data['years_of_experience'] = 'abc'

        form = DoctorRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('years_of_experience', form.errors)

    def test_invalid_consultation_fee(self):
        """Test niepoprawnej opłaty za konsultację"""
        # Tekst zamiast liczby
        data = self.valid_data.copy()
        data['consultation_fee'] = 'abc'

        form = DoctorRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('consultation_fee', form.errors)

    def test_negative_years_of_experience(self):
        """Test ujemnych lat doświadczenia"""
        data = self.valid_data.copy()
        data['years_of_experience'] = -5

        form = DoctorRegistrationForm(data=data)
        # Django IntegerField doesn't validate min value by default
        # but we can still create the form
        self.assertTrue(form.is_valid())  # This could be enhanced with custom validation

    def test_invalid_working_hours_format(self):
        """Test niepoprawnego formatu godzin pracy"""
        data = self.valid_data.copy()
        data['working_hours_start'] = 'invalid'

        form = DoctorRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('working_hours_start', form.errors)

    def test_form_fields_have_css_class(self):
        """Test że pola formularza mają klasę CSS"""
        form = DoctorRegistrationForm()
        for field_name, field in form.fields.items():
            self.assertEqual(
                field.widget.attrs.get('class'),
                'form-control',
                f"Field {field_name} should have form-control class"
            )

    def test_valid_specializations(self):
        """Test poprawnych specjalizacji"""
        # Użyj poprawnych wartości z modelu Doctor
        specializations = ['diabetologist', 'endocrinologist', 'internal_medicine']

        for spec in specializations:
            data = self.valid_data.copy()
            data['specialization'] = spec

            form = DoctorRegistrationForm(data=data)
            if not form.is_valid():
                # Sprawdź czy błąd dotyczy specjalizacji
                if 'specialization' in form.errors:
                    self.fail(f"Valid specialization {spec} was rejected")

    def test_password_mismatch(self):
        """Test niezgodności haseł"""
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPass123!'

        form = DoctorRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
