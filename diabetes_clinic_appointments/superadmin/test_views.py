"""
Integration tests for superadmin views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import date, timedelta
from authentication.models import User
from patients.models import Patient
from doctors.models import Doctor


class SuperadminDashboardViewTest(TestCase):
    """Test dashboard view for superadmin"""

    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('superadmin:dashboard')

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
            email='admin@test.com'
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='testpass123',
            user_type='patient'
        )

    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_dashboard_requires_superuser(self):
        """Test dashboard requires superuser status"""
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get(self.dashboard_url)

        # Should redirect to login (user_passes_test failed)
        self.assertEqual(response.status_code, 302)

    def test_dashboard_accessible_for_superuser(self):
        """Test dashboard is accessible for superuser"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'superadmin/dashboard.html')

    def test_dashboard_shows_statistics(self):
        """Test dashboard displays user statistics"""
        self.client.login(username='admin_test', password='testpass123')

        # Create test users
        patient_user = User.objects.create_user(
            username='patient1',
            password='pass',
            user_type='patient'
        )
        doctor_user = User.objects.create_user(
            username='doctor1',
            password='pass',
            user_type='doctor'
        )

        # Lock one account
        locked_user = User.objects.create_user(
            username='locked_user',
            password='pass'
        )
        locked_user.account_locked_until = timezone.now() + timedelta(hours=1)
        locked_user.save()

        response = self.client.get(self.dashboard_url)

        # Check statistics
        self.assertGreaterEqual(response.context['total_users'], 4)  # admin, regular, patient, doctor, locked
        self.assertGreaterEqual(response.context['total_patients'], 1)
        self.assertGreaterEqual(response.context['total_doctors'], 1)
        self.assertEqual(response.context['locked_accounts'], 1)


class SuperadminUserListViewTest(TestCase):
    """Test user_list view for superadmin"""

    def setUp(self):
        self.client = Client()
        self.user_list_url = reverse('superadmin:user_list')

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
            email='admin@test.com'
        )

        # Create test users
        self.patient = User.objects.create_user(
            username='patient1',
            password='pass',
            user_type='patient',
            first_name='Jan',
            last_name='Kowalski',
            email='jan@example.com'
        )

        self.doctor = User.objects.create_user(
            username='doctor1',
            password='pass',
            user_type='doctor',
            first_name='Anna',
            last_name='Nowak'
        )

        self.inactive_user = User.objects.create_user(
            username='inactive_user',
            password='pass',
            is_active=False
        )

        self.locked_user = User.objects.create_user(
            username='locked_user',
            password='pass'
        )
        self.locked_user.account_locked_until = timezone.now() + timedelta(hours=1)
        self.locked_user.save()

    def test_user_list_requires_superuser(self):
        """Test user list requires superuser status"""
        # Try without login
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, 302)

        # Try with regular user
        regular_user = User.objects.create_user(username='regular', password='pass')
        self.client.login(username='regular', password='pass')
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, 302)

    def test_user_list_accessible_for_superuser(self):
        """Test user list is accessible for superuser"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.user_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'superadmin/user_list.html')
        self.assertIn('users', response.context)

    def test_user_list_search(self):
        """Test user list search functionality"""
        self.client.login(username='admin_test', password='testpass123')

        # Search by username
        response = self.client.get(self.user_list_url + '?search=patient1')
        users = response.context['users']
        self.assertIn(self.patient, users)
        self.assertNotIn(self.doctor, users)

        # Search by first name
        response = self.client.get(self.user_list_url + '?search=Jan')
        users = response.context['users']
        self.assertIn(self.patient, users)

        # Search by email
        response = self.client.get(self.user_list_url + '?search=jan@example.com')
        users = response.context['users']
        self.assertIn(self.patient, users)

    def test_user_list_filter_by_type(self):
        """Test filtering users by type"""
        self.client.login(username='admin_test', password='testpass123')

        # Filter patients
        response = self.client.get(self.user_list_url + '?type=patient')
        users = response.context['users']
        self.assertIn(self.patient, users)
        self.assertNotIn(self.doctor, users)

        # Filter doctors
        response = self.client.get(self.user_list_url + '?type=doctor')
        users = response.context['users']
        self.assertIn(self.doctor, users)
        self.assertNotIn(self.patient, users)

    def test_user_list_filter_by_status(self):
        """Test filtering users by status"""
        self.client.login(username='admin_test', password='testpass123')

        # Filter active users
        response = self.client.get(self.user_list_url + '?status=active')
        users = response.context['users']
        self.assertNotIn(self.inactive_user, users)
        self.assertNotIn(self.locked_user, users)

        # Filter inactive users
        response = self.client.get(self.user_list_url + '?status=inactive')
        users = response.context['users']
        self.assertIn(self.inactive_user, users)

        # Filter locked users
        response = self.client.get(self.user_list_url + '?status=locked')
        users = response.context['users']
        self.assertIn(self.locked_user, users)


class SuperadminUserDetailViewTest(TestCase):
    """Test user_detail view for superadmin"""

    def setUp(self):
        self.client = Client()

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
            email='admin@test.com'
        )

        # Create patient with profile
        self.patient_user = User.objects.create_user(
            username='patient1',
            password='pass',
            user_type='patient'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Test 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='type1'
        )

        # Create doctor with profile
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            password='pass',
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

        self.patient_detail_url = reverse('superadmin:user_detail', kwargs={'user_id': self.patient_user.id})
        self.doctor_detail_url = reverse('superadmin:user_detail', kwargs={'user_id': self.doctor_user.id})

    def test_user_detail_requires_superuser(self):
        """Test user detail requires superuser status"""
        response = self.client.get(self.patient_detail_url)
        self.assertEqual(response.status_code, 302)

    def test_user_detail_accessible_for_superuser(self):
        """Test user detail is accessible for superuser"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.patient_detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'superadmin/user_detail.html')
        self.assertEqual(response.context['selected_user'], self.patient_user)

    def test_patient_detail_shows_patient_data(self):
        """Test patient detail shows patient profile data"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.patient_detail_url)

        self.assertIsNotNone(response.context['patient_data'])
        self.assertEqual(response.context['patient_data'], self.patient)
        self.assertIsNone(response.context['doctor_data'])

    def test_doctor_detail_shows_doctor_data(self):
        """Test doctor detail shows doctor profile data"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.doctor_detail_url)

        self.assertIsNotNone(response.context['doctor_data'])
        self.assertEqual(response.context['doctor_data'], self.doctor)
        self.assertIsNone(response.context['patient_data'])


class ToggleUserStatusViewTest(TestCase):
    """Test toggle_user_status view"""

    def setUp(self):
        self.client = Client()

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
            email='admin@test.com'
        )

        # Create test user
        self.test_user = User.objects.create_user(
            username='test_user',
            password='pass',
            is_active=True
        )

        self.toggle_url = reverse('superadmin:toggle_user_status', kwargs={'user_id': self.test_user.id})

    def test_toggle_requires_post(self):
        """Test toggle only works with POST"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.toggle_url)

        # Should redirect without making changes
        self.assertEqual(response.status_code, 302)

    def test_toggle_activates_inactive_user(self):
        """Test toggling activates inactive user"""
        self.client.login(username='admin_test', password='testpass123')

        # Make user inactive
        self.test_user.is_active = False
        self.test_user.save()

        response = self.client.post(self.toggle_url)

        # Verify user was activated
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.is_active)

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('aktywowane' in str(m) for m in messages))

    def test_toggle_deactivates_active_user(self):
        """Test toggling deactivates active user"""
        self.client.login(username='admin_test', password='testpass123')

        response = self.client.post(self.toggle_url)

        # Verify user was deactivated
        self.test_user.refresh_from_db()
        self.assertFalse(self.test_user.is_active)

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('dezaktywowane' in str(m) for m in messages))

    def test_cannot_deactivate_own_account(self):
        """Test superuser cannot deactivate their own account"""
        self.client.login(username='admin_test', password='testpass123')

        toggle_own_url = reverse('superadmin:toggle_user_status', kwargs={'user_id': self.superuser.id})
        response = self.client.post(toggle_own_url)

        # Verify account was not deactivated
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.is_active)

        # Verify error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('własnego konta' in str(m) for m in messages))


class UnlockUserAccountViewTest(TestCase):
    """Test unlock_user_account view"""

    def setUp(self):
        self.client = Client()

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
            email='admin@test.com'
        )

        # Create locked user
        self.locked_user = User.objects.create_user(
            username='locked_user',
            password='pass'
        )
        self.locked_user.failed_login_attempts = 5
        self.locked_user.account_locked_until = timezone.now() + timedelta(hours=1)
        self.locked_user.save()

        self.unlock_url = reverse('superadmin:unlock_user_account', kwargs={'user_id': self.locked_user.id})

    def test_unlock_requires_post(self):
        """Test unlock only works with POST"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.unlock_url)

        # Should redirect without making changes
        self.assertEqual(response.status_code, 302)

    def test_unlock_resets_failed_attempts(self):
        """Test unlocking resets failed login attempts"""
        self.client.login(username='admin_test', password='testpass123')

        response = self.client.post(self.unlock_url)

        # Verify account was unlocked
        self.locked_user.refresh_from_db()
        self.assertEqual(self.locked_user.failed_login_attempts, 0)
        self.assertIsNone(self.locked_user.account_locked_until)

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('odblokowane' in str(m) for m in messages))


class LockUserAccountViewTest(TestCase):
    """Test lock_user_account view"""

    def setUp(self):
        self.client = Client()

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
            email='admin@test.com'
        )

        # Create test user
        self.test_user = User.objects.create_user(
            username='test_user',
            password='pass'
        )

        self.lock_url = reverse('superadmin:lock_user_account', kwargs={'user_id': self.test_user.id})

    def test_lock_requires_post(self):
        """Test lock only works with POST"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.lock_url)

        # Should redirect without making changes
        self.assertEqual(response.status_code, 302)

    def test_lock_sets_lockout_time(self):
        """Test locking sets 24-hour lockout"""
        self.client.login(username='admin_test', password='testpass123')

        before_lock = timezone.now()
        response = self.client.post(self.lock_url)
        after_lock = timezone.now()

        # Verify account was locked
        self.test_user.refresh_from_db()
        self.assertIsNotNone(self.test_user.account_locked_until)

        # Verify lockout is approximately 24 hours
        expected_unlock = before_lock + timedelta(hours=24)
        self.assertGreater(self.test_user.account_locked_until, expected_unlock - timedelta(minutes=1))
        self.assertLess(self.test_user.account_locked_until, after_lock + timedelta(hours=24, minutes=1))

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('zablokowane na 24 godziny' in str(m) for m in messages))

    def test_cannot_lock_own_account(self):
        """Test superuser cannot lock their own account"""
        self.client.login(username='admin_test', password='testpass123')

        lock_own_url = reverse('superadmin:lock_user_account', kwargs={'user_id': self.superuser.id})
        response = self.client.post(lock_own_url)

        # Verify account was not locked
        self.superuser.refresh_from_db()
        self.assertIsNone(self.superuser.account_locked_until)

        # Verify error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('własnego konta' in str(m) for m in messages))


class ChangeUserRoleViewTest(TestCase):
    """Test change_user_role view"""

    def setUp(self):
        self.client = Client()

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
            email='admin@test.com'
        )

        # Create test user
        self.test_user = User.objects.create_user(
            username='test_user',
            password='pass',
            user_type='patient'
        )

        self.change_role_url = reverse('superadmin:change_user_role', kwargs={'user_id': self.test_user.id})

    def test_change_role_requires_post(self):
        """Test change role only works with POST"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.change_role_url)

        # Should redirect without making changes
        self.assertEqual(response.status_code, 302)

    def test_change_role_from_patient_to_doctor(self):
        """Test changing role from patient to doctor"""
        self.client.login(username='admin_test', password='testpass123')

        response = self.client.post(self.change_role_url, {
            'new_role': 'doctor'
        })

        # Verify role was changed
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.user_type, 'doctor')

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('zmieniona' in str(m) for m in messages))

    def test_change_role_from_doctor_to_patient(self):
        """Test changing role from doctor to patient"""
        self.client.login(username='admin_test', password='testpass123')

        self.test_user.user_type = 'doctor'
        self.test_user.save()

        response = self.client.post(self.change_role_url, {
            'new_role': 'patient'
        })

        # Verify role was changed
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.user_type, 'patient')

    def test_cannot_change_own_role(self):
        """Test superuser cannot change their own role"""
        self.client.login(username='admin_test', password='testpass123')

        # Get initial user_type
        initial_user_type = self.superuser.user_type

        change_own_url = reverse('superadmin:change_user_role', kwargs={'user_id': self.superuser.id})
        response = self.client.post(change_own_url, {
            'new_role': 'patient'
        })

        # Verify role was not changed
        self.superuser.refresh_from_db()
        self.assertEqual(self.superuser.user_type, initial_user_type)

        # Verify error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('własnego konta' in str(m) for m in messages))

    def test_reject_invalid_role(self):
        """Test rejecting invalid role"""
        self.client.login(username='admin_test', password='testpass123')

        response = self.client.post(self.change_role_url, {
            'new_role': 'invalid_role'
        })

        # Verify role was not changed
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.user_type, 'patient')

        # Verify error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Nieprawidłowa rola' in str(m) for m in messages))


class ToggleSuperuserStatusViewTest(TestCase):
    """Test toggle_superuser_status view"""

    def setUp(self):
        self.client = Client()

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
            email='admin@test.com'
        )

        # Create regular user
        self.test_user = User.objects.create_user(
            username='test_user',
            password='pass'
        )

        self.toggle_superuser_url = reverse('superadmin:toggle_superuser_status', kwargs={'user_id': self.test_user.id})

    def test_toggle_superuser_requires_post(self):
        """Test toggle superuser only works with POST"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.toggle_superuser_url)

        # Should redirect without making changes
        self.assertEqual(response.status_code, 302)

    def test_grant_superuser_status(self):
        """Test granting superuser status"""
        self.client.login(username='admin_test', password='testpass123')

        response = self.client.post(self.toggle_superuser_url)

        # Verify superuser status was granted
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.is_superuser)
        self.assertTrue(self.test_user.is_staff)

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('nadane' in str(m) for m in messages))

    def test_revoke_superuser_status(self):
        """Test revoking superuser status"""
        self.client.login(username='admin_test', password='testpass123')

        # Make user a superuser first
        self.test_user.is_superuser = True
        self.test_user.is_staff = True
        self.test_user.save()

        response = self.client.post(self.toggle_superuser_url)

        # Verify superuser status was revoked
        self.test_user.refresh_from_db()
        self.assertFalse(self.test_user.is_superuser)
        self.assertFalse(self.test_user.is_staff)

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('odebrane' in str(m) for m in messages))

    def test_cannot_revoke_own_superuser_status(self):
        """Test superuser cannot revoke their own superuser status"""
        self.client.login(username='admin_test', password='testpass123')

        toggle_own_url = reverse('superadmin:toggle_superuser_status', kwargs={'user_id': self.superuser.id})
        response = self.client.post(toggle_own_url)

        # Verify status was not changed
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.is_superuser)

        # Verify error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('sobie uprawnień' in str(m) for m in messages))


class DeleteUserViewTest(TestCase):
    """Test delete_user view"""

    def setUp(self):
        self.client = Client()

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
            email='admin@test.com'
        )

        # Create test user
        self.test_user = User.objects.create_user(
            username='test_user',
            password='pass'
        )

        self.delete_url = reverse('superadmin:delete_user', kwargs={'user_id': self.test_user.id})

    def test_delete_requires_post(self):
        """Test delete only works with POST"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.delete_url)

        # Should redirect without deleting
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(id=self.test_user.id).exists())

    def test_successful_user_deletion(self):
        """Test successful user deletion"""
        self.client.login(username='admin_test', password='testpass123')

        response = self.client.post(self.delete_url)

        # Verify user was deleted
        self.assertFalse(User.objects.filter(id=self.test_user.id).exists())

        # Verify redirect to user list
        self.assertRedirects(response, reverse('superadmin:user_list'))

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('usunięty' in str(m) for m in messages))

    def test_cannot_delete_own_account(self):
        """Test superuser cannot delete their own account"""
        self.client.login(username='admin_test', password='testpass123')

        delete_own_url = reverse('superadmin:delete_user', kwargs={'user_id': self.superuser.id})
        response = self.client.post(delete_own_url)

        # Verify account was not deleted
        self.assertTrue(User.objects.filter(id=self.superuser.id).exists())

        # Verify error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('własnego konta' in str(m) for m in messages))


class ResetUserPasswordViewTest(TestCase):
    """Test reset_user_password view"""

    def setUp(self):
        self.client = Client()

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
            email='admin@test.com'
        )

        # Create test user
        self.test_user = User.objects.create_user(
            username='test_user',
            password='oldpassword'
        )

        self.reset_password_url = reverse('superadmin:reset_user_password', kwargs={'user_id': self.test_user.id})

    def test_reset_password_requires_post(self):
        """Test reset password only works with POST"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(self.reset_password_url)

        # Should redirect without making changes
        self.assertEqual(response.status_code, 302)

    def test_successful_password_reset(self):
        """Test successful password reset"""
        self.client.login(username='admin_test', password='testpass123')

        response = self.client.post(self.reset_password_url, {
            'new_password': 'newpassword123'
        })

        # Verify password was changed
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password('newpassword123'))
        self.assertFalse(self.test_user.check_password('oldpassword'))

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('zresetowane' in str(m) for m in messages))

    def test_password_reset_requires_new_password(self):
        """Test password reset requires new password"""
        self.client.login(username='admin_test', password='testpass123')

        response = self.client.post(self.reset_password_url, {
            'new_password': ''
        })

        # Verify password was not changed
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password('oldpassword'))

        # Verify error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Podaj nowe hasło' in str(m) for m in messages))
