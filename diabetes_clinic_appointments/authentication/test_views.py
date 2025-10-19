"""
Integration tests for authentication views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import timedelta, date
from authentication.models import User
from patients.models import Patient


class LoginViewTest(TestCase):
    """Test login_view"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('authentication:login')

        # Create test users
        self.patient_user = User.objects.create_user(
            username='patient_test',
            password='testpass123',
            user_type='patient',
            first_name='Jan',
            last_name='Kowalski'
        )
        Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Test 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123456789',
            diabetes_type='healthy'
        )

        self.doctor_user = User.objects.create_user(
            username='doctor_test',
            password='testpass123',
            user_type='doctor'
        )

        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
            email='admin@test.com'
        )

    def test_login_page_get(self):
        """Test GET request shows login form"""
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')
        self.assertIn('form', response.context)

    def test_successful_patient_login(self):
        """Test successful login redirects patient to dashboard"""
        response = self.client.post(self.login_url, {
            'username': 'patient_test',
            'password': 'testpass123'
        })

        self.assertRedirects(response, reverse('patients:dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Verify failed login attempts were reset
        self.patient_user.refresh_from_db()
        self.assertEqual(self.patient_user.failed_login_attempts, 0)

    def test_successful_doctor_login(self):
        """Test successful login redirects doctor to dashboard"""
        # Create doctor profile for the doctor user
        from doctors.models import Doctor
        from datetime import time
        Doctor.objects.create(
            user=self.doctor_user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Lekarska 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        response = self.client.post(self.login_url, {
            'username': 'doctor_test',
            'password': 'testpass123'
        })

        self.assertRedirects(response, reverse('doctors:dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_successful_superuser_login(self):
        """Test successful login redirects superuser to admin dashboard"""
        response = self.client.post(self.login_url, {
            'username': 'admin_test',
            'password': 'testpass123'
        })

        self.assertRedirects(response, reverse('superadmin:dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_credentials(self):
        """Test login with invalid credentials shows error"""
        response = self.client.post(self.login_url, {
            'username': 'patient_test',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Nieprawidłowa nazwa użytkownika lub hasło' in str(m) for m in messages))

        # Verify failed login attempt was incremented
        self.patient_user.refresh_from_db()
        self.assertEqual(self.patient_user.failed_login_attempts, 1)

    def test_account_lockout_after_5_attempts(self):
        """Test account locks after 5 failed login attempts"""
        # Make 5 failed login attempts
        for i in range(5):
            self.client.post(self.login_url, {
                'username': 'patient_test',
                'password': 'wrongpassword'
            })

        self.patient_user.refresh_from_db()
        self.assertEqual(self.patient_user.failed_login_attempts, 5)
        self.assertTrue(self.patient_user.is_account_locked())

        # Try to login with correct password - should be blocked
        response = self.client.post(self.login_url, {
            'username': 'patient_test',
            'password': 'testpass123'
        })

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('zablokowane' in str(m) for m in messages))

    def test_remaining_attempts_message(self):
        """Test message shows remaining attempts"""
        # Make 2 failed attempts
        for i in range(2):
            response = self.client.post(self.login_url, {
                'username': 'patient_test',
                'password': 'wrongpassword'
            })

        messages = list(get_messages(response.wsgi_request))
        # Should show 3 remaining attempts (5 - 2)
        self.assertTrue(any('Pozostało prób: 3' in str(m) for m in messages))

    def test_nonexistent_user_login(self):
        """Test login with non-existent username"""
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'somepassword'
        })

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Nieprawidłowa nazwa użytkownika lub hasło' in str(m) for m in messages))


class RegisterPatientViewTest(TestCase):
    """Test register_patient view"""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('authentication:register_patient')

    def test_register_page_get(self):
        """Test GET request shows registration form"""
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/register_patient.html')
        self.assertIn('form', response.context)

    def test_successful_registration(self):
        """Test successful patient registration"""
        response = self.client.post(self.register_url, {
            'username': 'newpatient',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@example.com',
            'phone_number': '123456789',
            'date_of_birth': '1992-03-21',
            'pesel': '92032109552',
            'address': 'ul. Testowa 1, Warszawa',
            'emergency_contact_name': 'Anna Kowalska',
            'emergency_contact_phone': '987654321',
            'diabetes_type': 'healthy',
        })

        self.assertRedirects(response, reverse('authentication:login'))

        # Verify user was created
        user = User.objects.get(username='newpatient')
        self.assertEqual(user.user_type, 'patient')
        self.assertTrue(hasattr(user, 'patient_profile'))

        # Verify patient profile was created
        patient = user.patient_profile
        self.assertEqual(patient.pesel, '92032109552')

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('utworzone pomyślnie' in str(m) for m in messages))

    def test_registration_with_invalid_pesel(self):
        """Test registration fails with invalid PESEL checksum"""
        response = self.client.post(self.register_url, {
            'username': 'newpatient',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@example.com',
            'date_of_birth': '1992-03-21',
            'pesel': '92032109559',  # Invalid checksum
            'address': 'ul. Testowa 1',
            'emergency_contact_name': 'Test',
            'emergency_contact_phone': '123',
            'diabetes_type': 'healthy',
        })

        self.assertEqual(response.status_code, 200)
        # Check if form has errors for 'pesel' field
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('pesel', response.context['form'].errors)
        self.assertIn('PESEL jest nieprawidłowy', str(response.context['form'].errors['pesel']))

    def test_registration_with_mismatched_birth_date(self):
        """Test registration fails when birth date doesn't match PESEL"""
        response = self.client.post(self.register_url, {
            'username': 'newpatient',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@example.com',
            'date_of_birth': '1992-03-22',  # Wrong day
            'pesel': '92032109552',  # PESEL for 1992-03-21
            'address': 'ul. Testowa 1',
            'emergency_contact_name': 'Test',
            'emergency_contact_phone': '123',
            'diabetes_type': 'healthy',
        })

        self.assertEqual(response.status_code, 200)
        # Should have form error
        self.assertFalse(response.context['form'].is_valid())

    def test_registration_with_duplicate_pesel(self):
        """Test registration fails with duplicate PESEL"""
        # Create existing patient
        existing_user = User.objects.create_user(
            username='existing',
            password='pass'
        )
        Patient.objects.create(
            user=existing_user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Test 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='healthy'
        )

        # Try to register with same PESEL
        response = self.client.post(self.register_url, {
            'username': 'newpatient',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@example.com',
            'date_of_birth': '1992-03-21',
            'pesel': '92032109552',  # Duplicate PESEL
            'address': 'ul. Testowa 1',
            'emergency_contact_name': 'Test',
            'emergency_contact_phone': '123',
            'diabetes_type': 'healthy',
        })

        self.assertEqual(response.status_code, 200)
        # Should show form again with error
        self.assertIn('form', response.context)


class LogoutViewTest(TestCase):
    """Test logout_view"""

    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('authentication:logout')

        # Create and login a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_logout_redirects_unauthenticated(self):
        """Test logout view requires login"""
        response = self.client.get(self.logout_url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_successful_logout(self):
        """Test successful logout"""
        # Login first
        self.client.login(username='testuser', password='testpass123')

        # Logout
        response = self.client.get(self.logout_url, follow=True)

        # Verify user is logged out
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('wylogowany' in str(m) for m in messages))
