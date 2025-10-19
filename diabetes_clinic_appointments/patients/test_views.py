"""
Integration tests for patients views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import date, timedelta
from authentication.models import User
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment


class PatientDashboardViewTest(TestCase):
    """Test dashboard view for patients"""

    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('patients:dashboard')

        # Create patient user
        self.patient_user = User.objects.create_user(
            username='patient_test',
            password='testpass123',
            user_type='patient'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Test 1',
            emergency_contact_name='Test Contact',
            emergency_contact_phone='123456789',
            diabetes_type='type1'
        )

        # Create doctor for appointments
        self.doctor_user = User.objects.create_user(
            username='doctor_test',
            password='testpass123',
            user_type='doctor'
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Lekarska 1',
            consultation_fee=200.00,
            working_hours_start='08:00',
            working_hours_end='16:00',
            education='Medical University'
        )

    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(self.dashboard_url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_dashboard_accessible_for_patient(self):
        """Test dashboard is accessible for logged-in patient"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patients/dashboard.html')
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], self.patient)

    def test_dashboard_redirects_doctor(self):
        """Test dashboard redirects doctor users"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.dashboard_url)

        self.assertRedirects(response, reverse('authentication:login'))

    def test_dashboard_shows_statistics(self):
        """Test dashboard displays appointment statistics"""
        self.client.login(username='patient_test', password='testpass123')

        # Create appointments
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=10),
            reason='Past visit',
            status='completed'
        )
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=5),
            reason='Future visit',
            status='scheduled'
        )

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.context['total_appointments'], 2)
        self.assertEqual(response.context['upcoming_count'], 1)
        self.assertIsNotNone(response.context['next_appointment'])
        self.assertIsNotNone(response.context['last_appointment'])

    def test_dashboard_shows_cooldown_info(self):
        """Test dashboard shows cooldown info after cancellation"""
        self.client.login(username='patient_test', password='testpass123')

        # Set recent cancellation
        self.patient.last_cancellation_time = timezone.now()
        self.patient.save()

        response = self.client.get(self.dashboard_url)

        self.assertIsNotNone(response.context['cooldown_info'])
        self.assertTrue(response.context['cooldown_info']['active'])
        self.assertIn('minutes', response.context['cooldown_info'])
        self.assertIn('seconds', response.context['cooldown_info'])

    def test_dashboard_no_cooldown_initially(self):
        """Test dashboard shows no cooldown for new patient"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.dashboard_url)

        self.assertIsNone(response.context['cooldown_info'])


class PatientProfileViewTest(TestCase):
    """Test profile view for patients"""

    def setUp(self):
        self.client = Client()
        self.profile_url = reverse('patients:profile')

        # Create patient user
        self.patient_user = User.objects.create_user(
            username='patient_test',
            password='testpass123',
            user_type='patient',
            first_name='Jan',
            last_name='Kowalski'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Test 1',
            emergency_contact_name='Test Contact',
            emergency_contact_phone='123456789',
            diabetes_type='type1'
        )

        # Create doctor for appointments
        self.doctor_user = User.objects.create_user(
            username='doctor_test',
            password='testpass123',
            user_type='doctor'
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Lekarska 1',
            consultation_fee=200.00,
            working_hours_start='08:00',
            working_hours_end='16:00',
            education='Medical University'
        )

    def test_profile_requires_login(self):
        """Test profile requires authentication"""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_profile_accessible_for_patient(self):
        """Test profile is accessible for logged-in patient"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patients/profile.html')
        self.assertIn('patient', response.context)
        self.assertEqual(response.context['patient'], self.patient)

    def test_profile_redirects_doctor(self):
        """Test profile redirects doctor users"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.profile_url)

        self.assertRedirects(response, reverse('authentication:login'))

    def test_profile_displays_patient_data(self):
        """Test profile displays all patient information"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.profile_url)

        # Check context contains expected data
        self.assertIn('age', response.context)
        self.assertIn('total_appointments', response.context)
        self.assertIn('last_appointment', response.context)
        self.assertIn('next_appointment', response.context)

        # Verify age calculation
        expected_age = self.patient.get_age()
        self.assertEqual(response.context['age'], expected_age)

    def test_profile_shows_appointment_statistics(self):
        """Test profile shows appointment statistics"""
        self.client.login(username='patient_test', password='testpass123')

        # Create appointments
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=30),
            reason='Past visit',
            status='completed'
        )
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=7),
            reason='Future visit',
            status='scheduled'
        )

        response = self.client.get(self.profile_url)

        self.assertEqual(response.context['total_appointments'], 2)
        self.assertIsNotNone(response.context['last_appointment'])
        self.assertIsNotNone(response.context['next_appointment'])


class PatientEditProfileViewTest(TestCase):
    """Test edit_profile view for patients"""

    def setUp(self):
        self.client = Client()
        self.edit_profile_url = reverse('patients:edit_profile')

        # Create patient user
        self.patient_user = User.objects.create_user(
            username='patient_test',
            password='testpass123',
            user_type='patient',
            first_name='Jan',
            last_name='Kowalski',
            email='jan@example.com'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Testowa 1, Warszawa',
            emergency_contact_name='Anna Kowalska',
            emergency_contact_phone='123456789',
            diabetes_type='type1',
            current_medications='Insulin',
            allergies='None'
        )

    def test_edit_profile_requires_login(self):
        """Test edit profile requires authentication"""
        response = self.client.get(self.edit_profile_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_edit_profile_get_shows_form(self):
        """Test GET request shows edit form with current data"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.edit_profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patients/edit_profile.html')
        self.assertIn('form', response.context)
        self.assertIn('patient', response.context)

    def test_edit_profile_redirects_doctor(self):
        """Test edit profile redirects doctor users"""
        doctor_user = User.objects.create_user(
            username='doctor_test',
            password='testpass123',
            user_type='doctor'
        )
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.edit_profile_url)

        self.assertRedirects(response, reverse('authentication:login'))

    def test_successful_profile_update(self):
        """Test successful profile update"""
        self.client.login(username='patient_test', password='testpass123')

        updated_data = {
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan.new@example.com',
            'phone_number': '987654321',
            'address': 'ul. Nowa 5, Kraków',
            'emergency_contact_name': 'Piotr Kowalski',
            'emergency_contact_phone': '555666777',
            'current_medications': 'Insulin + Metformin',
            'allergies': 'Penicillin'
        }

        response = self.client.post(self.edit_profile_url, updated_data)

        self.assertRedirects(response, reverse('patients:profile'))

        # Verify changes were saved
        self.patient.refresh_from_db()
        self.patient_user.refresh_from_db()

        self.assertEqual(self.patient_user.email, 'jan.new@example.com')
        self.assertEqual(self.patient_user.phone_number, '987654321')
        self.assertEqual(self.patient.address, 'ul. Nowa 5, Kraków')
        self.assertEqual(self.patient.emergency_contact_name, 'Piotr Kowalski')
        self.assertEqual(self.patient.current_medications, 'Insulin + Metformin')

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('zaktualizowany' in str(m) for m in messages))

    def test_edit_profile_validation_error(self):
        """Test edit profile with invalid data shows error"""
        self.client.login(username='patient_test', password='testpass123')

        invalid_data = {
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'invalid-email',  # Invalid email
            'phone_number': '123',
            'address': 'ul. Test 1',
            'emergency_contact_name': 'Test',
            'emergency_contact_phone': '123',
        }

        response = self.client.post(self.edit_profile_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patients/edit_profile.html')

        # Verify error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('poprawność' in str(m) for m in messages))

    def test_edit_profile_preserves_readonly_fields(self):
        """Test that PESEL and date_of_birth cannot be changed"""
        self.client.login(username='patient_test', password='testpass123')

        # Try to change PESEL and birth date (should be ignored by form)
        data = {
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@example.com',
            'phone_number': '123456789',
            'address': 'ul. Test 1',
            'emergency_contact_name': 'Test',
            'emergency_contact_phone': '123',
            'pesel': '00210155875',  # Try to change PESEL
            'date_of_birth': '2000-01-01',  # Try to change birth date
        }

        response = self.client.post(self.edit_profile_url, data)

        # Verify PESEL and birth date were NOT changed
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.pesel, '92032109552')  # Original PESEL
        self.assertEqual(self.patient.date_of_birth, date(1992, 3, 21))  # Original date
