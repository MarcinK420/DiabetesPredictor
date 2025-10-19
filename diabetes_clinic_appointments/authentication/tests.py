"""
Tests for User model.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import User


class UserCreationTest(TestCase):
    """Test User model creation"""

    def test_create_patient_user(self):
        """Test creating a patient user"""
        user = User.objects.create_user(
            username='patient1',
            password='testpass123',
            user_type='patient',
            first_name='Jan',
            last_name='Kowalski',
            email='jan@example.com'
        )
        self.assertEqual(user.username, 'patient1')
        self.assertEqual(user.user_type, 'patient')
        self.assertTrue(user.is_patient())
        self.assertFalse(user.is_doctor())

    def test_create_doctor_user(self):
        """Test creating a doctor user"""
        user = User.objects.create_user(
            username='doctor1',
            password='testpass123',
            user_type='doctor',
            first_name='Anna',
            last_name='Nowak',
            email='anna@example.com'
        )
        self.assertEqual(user.username, 'doctor1')
        self.assertEqual(user.user_type, 'doctor')
        self.assertTrue(user.is_doctor())
        self.assertFalse(user.is_patient())

    def test_default_user_type(self):
        """Test that default user_type is 'patient'"""
        user = User.objects.create_user(
            username='defaultuser',
            password='testpass123'
        )
        self.assertEqual(user.user_type, 'patient')
        self.assertTrue(user.is_patient())


class UserTypeMethodsTest(TestCase):
    """Test is_patient() and is_doctor() methods"""

    def setUp(self):
        self.patient = User.objects.create_user(
            username='patient',
            password='pass',
            user_type='patient'
        )
        self.doctor = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )

    def test_is_patient_method(self):
        """Test is_patient() returns correct value"""
        self.assertTrue(self.patient.is_patient())
        self.assertFalse(self.doctor.is_patient())

    def test_is_doctor_method(self):
        """Test is_doctor() returns correct value"""
        self.assertTrue(self.doctor.is_doctor())
        self.assertFalse(self.patient.is_doctor())


class AccountLockingTest(TestCase):
    """Test account locking mechanism"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_account_not_locked_initially(self):
        """Test that account is not locked initially"""
        self.assertFalse(self.user.is_account_locked())
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNone(self.user.account_locked_until)

    def test_increment_failed_login(self):
        """Test incrementing failed login attempts"""
        initial_time = timezone.now()

        self.user.increment_failed_login()
        self.user.refresh_from_db()

        self.assertEqual(self.user.failed_login_attempts, 1)
        self.assertIsNotNone(self.user.last_failed_login)
        self.assertIsNone(self.user.account_locked_until)
        self.assertFalse(self.user.is_account_locked())

    def test_account_locked_after_5_attempts(self):
        """Test that account is locked after 5 failed attempts"""
        # Simulate 5 failed login attempts
        for i in range(5):
            self.user.increment_failed_login()

        self.user.refresh_from_db()

        self.assertEqual(self.user.failed_login_attempts, 5)
        self.assertIsNotNone(self.user.account_locked_until)
        self.assertTrue(self.user.is_account_locked())

    def test_account_locked_for_15_minutes(self):
        """Test that account is locked for 15 minutes"""
        # Lock the account
        for i in range(5):
            self.user.increment_failed_login()

        self.user.refresh_from_db()

        # Check that lock is approximately 15 minutes in the future
        expected_unlock_time = timezone.now() + timedelta(minutes=15)
        time_difference = abs((self.user.account_locked_until - expected_unlock_time).total_seconds())

        # Allow 5 seconds tolerance
        self.assertLess(time_difference, 5)

    def test_account_auto_unlocks_after_time(self):
        """Test that account automatically unlocks after lock period"""
        # Lock the account
        for i in range(5):
            self.user.increment_failed_login()

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_account_locked())

        # Simulate time passing (set lock time in the past)
        self.user.account_locked_until = timezone.now() - timedelta(minutes=1)
        self.user.save()

        # Check if account is unlocked
        self.assertFalse(self.user.is_account_locked())

        # Verify that failed attempts were reset
        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNone(self.user.account_locked_until)

    def test_reset_failed_login(self):
        """Test resetting failed login attempts"""
        # Add some failed attempts
        for i in range(3):
            self.user.increment_failed_login()

        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 3)

        # Reset
        self.user.reset_failed_login()
        self.user.refresh_from_db()

        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNone(self.user.last_failed_login)
        self.assertIsNone(self.user.account_locked_until)
        self.assertFalse(self.user.is_account_locked())

    def test_reset_locked_account(self):
        """Test resetting a locked account"""
        # Lock the account
        for i in range(5):
            self.user.increment_failed_login()

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_account_locked())

        # Reset
        self.user.reset_failed_login()
        self.user.refresh_from_db()

        self.assertFalse(self.user.is_account_locked())
        self.assertEqual(self.user.failed_login_attempts, 0)


class UserPhoneNumberTest(TestCase):
    """Test phone_number field"""

    def test_phone_number_optional(self):
        """Test that phone_number is optional"""
        user = User.objects.create_user(
            username='user1',
            password='pass'
        )
        self.assertEqual(user.phone_number, '')

    def test_phone_number_can_be_set(self):
        """Test setting phone_number"""
        user = User.objects.create_user(
            username='user2',
            password='pass',
            phone_number='123456789'
        )
        self.assertEqual(user.phone_number, '123456789')
