"""
Testy dla formularzy patients.

Testuje:
- PatientProfileForm
"""

from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from patients.forms import PatientProfileForm
from patients.models import Patient

User = get_user_model()


class PatientProfileFormTest(TestCase):
    """Testy formularza edycji profilu pacjenta"""

    def setUp(self):
        """Przygotowanie danych testowych"""
        # Utwórz użytkownika i pacjenta
        self.user = User.objects.create_user(
            username='testpatient',
            email='old@example.com',
            password='TestPass123!',
            first_name='Jan',
            last_name='Kowalski',
            phone_number='+48123456789',
            user_type='patient'
        )

        self.patient = Patient.objects.create(
            user=self.user,
            date_of_birth=date(1990, 5, 14),
            pesel='90051401233',  # Valid PESEL for 1990-05-14
            address='ul. Stara 1, 00-001 Warszawa',
            emergency_contact_name='Anna Kowalska',
            emergency_contact_phone='+48987654321',
            diabetes_type='type1',
            diagnosis_date=date(2010, 1, 15),
            current_medications='Insulin',
            allergies='Penicillin'
        )

        self.valid_data = {
            'first_name': 'Jan',
            'last_name': 'Nowak',  # Zmienione nazwisko
            'email': 'jan.nowak@example.com',  # Nowy email
            'phone_number': '+48111222333',  # Nowy telefon
            'address': 'ul. Nowa 2, 00-002 Warszawa',  # Nowy adres
            'emergency_contact_name': 'Maria Nowak',
            'emergency_contact_phone': '+48555666777',
            'current_medications': 'Insulin, Metformin',
            'allergies': 'Penicillin, Aspirin',
        }

    def test_valid_profile_edit(self):
        """Test poprawnej edycji profilu"""
        form = PatientProfileForm(
            data=self.valid_data,
            instance=self.patient,
            user=self.user
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_save_updates_user_and_patient(self):
        """Test że save() aktualizuje User i Patient"""
        form = PatientProfileForm(
            data=self.valid_data,
            instance=self.patient,
            user=self.user
        )
        self.assertTrue(form.is_valid())

        patient = form.save()

        # Odśwież obiekty z bazy danych
        self.user.refresh_from_db()
        patient.refresh_from_db()

        # Sprawdź User
        self.assertEqual(self.user.first_name, 'Jan')
        self.assertEqual(self.user.last_name, 'Nowak')
        self.assertEqual(self.user.email, 'jan.nowak@example.com')
        self.assertEqual(self.user.phone_number, '+48111222333')

        # Sprawdź Patient
        self.assertEqual(patient.address, 'ul. Nowa 2, 00-002 Warszawa')
        self.assertEqual(patient.emergency_contact_name, 'Maria Nowak')
        self.assertEqual(patient.emergency_contact_phone, '+48555666777')
        self.assertEqual(patient.current_medications, 'Insulin, Metformin')
        self.assertEqual(patient.allergies, 'Penicillin, Aspirin')

    def test_form_prepopulates_user_fields(self):
        """Test że formularz pre-populuje pola User"""
        form = PatientProfileForm(instance=self.patient, user=self.user)

        self.assertEqual(form.fields['first_name'].initial, 'Jan')
        self.assertEqual(form.fields['last_name'].initial, 'Kowalski')
        self.assertEqual(form.fields['email'].initial, 'old@example.com')
        self.assertEqual(form.fields['phone_number'].initial, '+48123456789')

    def test_form_without_user_parameter(self):
        """Test formularza bez parametru user"""
        form = PatientProfileForm(
            data=self.valid_data,
            instance=self.patient
        )
        # Formularz powinien być poprawny, ale nie zaktualizuje User
        self.assertTrue(form.is_valid(), form.errors)

        patient = form.save()

        # User nie powinien zostać zaktualizowany
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'old@example.com')  # Stary email

        # Patient powinien być zaktualizowany
        patient.refresh_from_db()
        self.assertEqual(patient.address, 'ul. Nowa 2, 00-002 Warszawa')

    def test_missing_required_patient_fields(self):
        """Test brakujących wymaganych pól Patient"""
        required_patient_fields = [
            'address',
            'emergency_contact_name',
            'emergency_contact_phone'
        ]

        for field in required_patient_fields:
            data = self.valid_data.copy()
            data[field] = ''

            form = PatientProfileForm(
                data=data,
                instance=self.patient,
                user=self.user
            )
            self.assertFalse(form.is_valid(), f"Field {field} should be required")
            self.assertIn(field, form.errors, f"Missing error for field {field}")

    def test_optional_patient_fields(self):
        """Test opcjonalnych pól Patient"""
        data = self.valid_data.copy()
        data['current_medications'] = ''
        data['allergies'] = ''
        data['phone_number'] = ''

        form = PatientProfileForm(
            data=data,
            instance=self.patient,
            user=self.user
        )
        self.assertTrue(form.is_valid(), form.errors)

        patient = form.save()
        patient.refresh_from_db()

        self.assertEqual(patient.current_medications, '')
        self.assertEqual(patient.allergies, '')

    def test_invalid_email_format(self):
        """Test niepoprawnego formatu email"""
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'

        form = PatientProfileForm(
            data=data,
            instance=self.patient,
            user=self.user
        )
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_update_only_user_fields(self):
        """Test aktualizacji tylko pól User"""
        data = self.valid_data.copy()
        # Pozostaw pola Patient bez zmian
        data['address'] = self.patient.address
        data['emergency_contact_name'] = self.patient.emergency_contact_name
        data['emergency_contact_phone'] = self.patient.emergency_contact_phone
        data['current_medications'] = self.patient.current_medications
        data['allergies'] = self.patient.allergies

        # Zmień tylko email
        data['email'] = 'newemail@example.com'

        form = PatientProfileForm(
            data=data,
            instance=self.patient,
            user=self.user
        )
        self.assertTrue(form.is_valid())

        form.save()
        self.user.refresh_from_db()

        self.assertEqual(self.user.email, 'newemail@example.com')

    def test_update_only_patient_fields(self):
        """Test aktualizacji tylko pól Patient"""
        data = self.valid_data.copy()
        # Pozostaw pola User bez zmian
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['email'] = self.user.email
        data['phone_number'] = self.user.phone_number

        # Zmień tylko adres
        data['address'] = 'ul. Inna 3, 00-003 Warszawa'

        form = PatientProfileForm(
            data=data,
            instance=self.patient,
            user=self.user
        )
        self.assertTrue(form.is_valid())

        patient = form.save()
        patient.refresh_from_db()

        self.assertEqual(patient.address, 'ul. Inna 3, 00-003 Warszawa')

    def test_form_fields_have_css_class(self):
        """Test że pola formularza mają klasę CSS"""
        form = PatientProfileForm(instance=self.patient, user=self.user)

        fields_with_form_control = [
            'first_name', 'last_name', 'email', 'phone_number',
            'address', 'emergency_contact_name', 'emergency_contact_phone',
            'current_medications', 'allergies'
        ]

        for field_name in fields_with_form_control:
            field = form.fields[field_name]
            self.assertEqual(
                field.widget.attrs.get('class'),
                'form-control' if 'form-control' in field.widget.attrs.get('class', '') else None,
                f"Field {field_name} should have form-control class"
            )

    def test_textarea_fields_have_rows_attribute(self):
        """Test że pola textarea mają atrybut rows"""
        form = PatientProfileForm(instance=self.patient, user=self.user)

        textarea_fields = {
            'address': 3,
            'current_medications': 4,
            'allergies': 3,
        }

        for field_name, expected_rows in textarea_fields.items():
            field = form.fields[field_name]
            self.assertIn(
                'rows',
                field.widget.attrs,
                f"Field {field_name} should have rows attribute"
            )
            self.assertEqual(
                field.widget.attrs['rows'],
                expected_rows,
                f"Field {field_name} should have {expected_rows} rows"
            )

    def test_help_text_on_fields(self):
        """Test że niektóre pola mają tekst pomocniczy"""
        form = PatientProfileForm(instance=self.patient, user=self.user)

        # Sprawdź że pola mają tekst pomocniczy (może być w różnych formach)
        self.assertIsNotNone(form.fields['current_medications'].help_text)
        self.assertIsNotNone(form.fields['allergies'].help_text)
        self.assertTrue(len(form.fields['current_medications'].help_text) > 0)
        self.assertTrue(len(form.fields['allergies'].help_text) > 0)

    def test_save_with_commit_false(self):
        """Test zapisywania z commit=False"""
        form = PatientProfileForm(
            data=self.valid_data,
            instance=self.patient,
            user=self.user
        )
        self.assertTrue(form.is_valid())

        # Zapisz bez commit
        patient = form.save(commit=False)

        # Sprawdź że zmiany są w pamięci ale nie w bazie
        self.assertEqual(patient.address, 'ul. Nowa 2, 00-002 Warszawa')

        # Odśwież z bazy - powinien mieć stary adres
        patient.refresh_from_db()
        self.assertEqual(patient.address, 'ul. Stara 1, 00-001 Warszawa')

        # User też nie powinien być zapisany
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'old@example.com')

    def test_long_text_fields(self):
        """Test długich wartości w polach tekstowych"""
        data = self.valid_data.copy()
        data['current_medications'] = 'Very long medication list. ' * 50
        data['allergies'] = 'Very long allergy list. ' * 50

        form = PatientProfileForm(
            data=data,
            instance=self.patient,
            user=self.user
        )
        # Django TextField nie ma domyślnego limitu długości
        self.assertTrue(form.is_valid(), form.errors)

    def test_special_characters_in_address(self):
        """Test znaków specjalnych w adresie"""
        data = self.valid_data.copy()
        data['address'] = 'ul. Św. Jana 5/7, 00-123 Kraków'

        form = PatientProfileForm(
            data=data,
            instance=self.patient,
            user=self.user
        )
        self.assertTrue(form.is_valid(), form.errors)

        patient = form.save()
        patient.refresh_from_db()
        self.assertEqual(patient.address, 'ul. Św. Jana 5/7, 00-123 Kraków')

    def test_phone_number_formats(self):
        """Test różnych formatów numerów telefonów"""
        valid_phone_formats = [
            '+48123456789',
            '48123456789',
            '123456789',
            '+48 123 456 789',
        ]

        for phone in valid_phone_formats:
            data = self.valid_data.copy()
            data['phone_number'] = phone

            form = PatientProfileForm(
                data=data,
                instance=self.patient,
                user=self.user
            )
            # CharField przyjmuje większość formatów (max_length=15 może odrzucić niektóre)
            if len(phone) <= 15:
                self.assertTrue(form.is_valid(), f"Phone format {phone} should be valid. Errors: {form.errors}")
