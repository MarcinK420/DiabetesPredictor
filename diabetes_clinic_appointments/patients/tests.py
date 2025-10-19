"""
Tests for Patient model.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from authentication.models import User
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment


class PatientCreationTest(TestCase):
    """Test Patient model creation"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='patient1',
            password='testpass123',
            user_type='patient',
            first_name='Jan',
            last_name='Kowalski'
        )

    def test_create_patient_with_valid_pesel(self):
        """Test creating patient with valid PESEL"""
        patient = Patient.objects.create(
            user=self.user,
            date_of_birth=date(1944, 5, 14),
            pesel='44051401458',
            address='ul. Testowa 1, Warszawa',
            emergency_contact_name='Anna Kowalska',
            emergency_contact_phone='123456789',
            diabetes_type='type1',
            diagnosis_date=date(2020, 1, 15)
        )
        self.assertEqual(patient.user, self.user)
        self.assertEqual(patient.pesel, '44051401458')
        self.assertEqual(patient.diabetes_type, 'type1')

    def test_pesel_must_be_unique(self):
        """Test that PESEL must be unique"""
        Patient.objects.create(
            user=self.user,
            date_of_birth=date(1944, 5, 14),
            pesel='44051401458',
            address='ul. Testowa 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='healthy'
        )

        # Create another user
        user2 = User.objects.create_user(
            username='patient2',
            password='pass',
            user_type='patient'
        )

        # Try to create patient with same PESEL
        patient2 = Patient(
            user=user2,
            date_of_birth=date(1944, 5, 14),
            pesel='44051401458',  # Same PESEL
            address='ul. Inna 2',
            emergency_contact_name='Test2',
            emergency_contact_phone='456',
            diabetes_type='healthy'
        )

        with self.assertRaises(Exception):  # Will raise IntegrityError or ValidationError
            patient2.save()

    def test_create_healthy_patient(self):
        """Test creating healthy patient (no diabetes)"""
        patient = Patient.objects.create(
            user=self.user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Testowa 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='healthy'
        )
        self.assertEqual(patient.diabetes_type, 'healthy')
        self.assertIsNone(patient.diagnosis_date)


class PatientStrMethodTest(TestCase):
    """Test Patient __str__ method"""

    def test_patient_str_representation(self):
        """Test string representation of patient"""
        user = User.objects.create_user(
            username='patient',
            password='pass',
            first_name='Jan',
            last_name='Kowalski'
        )
        patient = Patient.objects.create(
            user=user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Testowa 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='type1'
        )
        self.assertEqual(str(patient), 'Jan Kowalski - Cukrzyca typu 1')


class PatientBookingRestrictionsTest(TestCase):
    """Test appointment booking restrictions (2-minute cooldown)"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='patient',
            password='pass',
            user_type='patient'
        )
        self.patient = Patient.objects.create(
            user=self.user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Testowa 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='healthy'
        )

    def test_can_book_appointment_initially(self):
        """Test that patient can book appointment initially"""
        self.assertTrue(self.patient.can_book_appointment())
        self.assertIsNone(self.patient.time_until_can_book())

    def test_cannot_book_within_2_minutes_of_cancellation(self):
        """Test that patient cannot book within 2 minutes of cancellation"""
        # Set cancellation time to now
        self.patient.last_cancellation_time = timezone.now()
        self.patient.save()

        self.assertFalse(self.patient.can_book_appointment())
        self.assertIsNotNone(self.patient.time_until_can_book())

    def test_can_book_after_2_minutes(self):
        """Test that patient can book after 2 minutes"""
        # Set cancellation time to 3 minutes ago
        self.patient.last_cancellation_time = timezone.now() - timedelta(minutes=3)
        self.patient.save()

        self.assertTrue(self.patient.can_book_appointment())
        self.assertIsNone(self.patient.time_until_can_book())

    def test_time_until_can_book_calculation(self):
        """Test calculation of remaining time"""
        # Set cancellation to 1 minute ago
        self.patient.last_cancellation_time = timezone.now() - timedelta(minutes=1)
        self.patient.save()

        remaining = self.patient.time_until_can_book()
        self.assertIsNotNone(remaining)

        # Should be approximately 1 minute remaining (allow 5 second tolerance)
        self.assertGreater(remaining.total_seconds(), 55)
        self.assertLess(remaining.total_seconds(), 65)


class PatientAgeCalculationTest(TestCase):
    """Test age calculation"""

    def test_get_age(self):
        """Test age calculation for various birth dates"""
        user = User.objects.create_user(username='patient', password='pass')

        # Patient born on 1992-03-21
        patient = Patient.objects.create(
            user=user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Testowa 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='healthy'
        )

        today = timezone.now().date()
        expected_age = today.year - 1992

        # Adjust if birthday hasn't occurred this year
        if (today.month, today.day) < (3, 21):
            expected_age -= 1

        self.assertEqual(patient.get_age(), expected_age)

    def test_get_age_for_child(self):
        """Test age calculation for young patient"""
        user = User.objects.create_user(username='child', password='pass')

        # Patient born 5 years ago
        five_years_ago = timezone.now().date() - timedelta(days=5*365)

        patient = Patient.objects.create(
            user=user,
            date_of_birth=five_years_ago,
            pesel='00210155875',  # Using valid PESEL
            address='ul. Testowa 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='healthy'
        )

        age = patient.get_age()
        self.assertIn(age, [4, 5])  # Could be 4 or 5 depending on exact date


class PatientMaskingTest(TestCase):
    """Test PESEL and phone masking"""

    def setUp(self):
        user = User.objects.create_user(username='patient', password='pass')
        self.patient = Patient.objects.create(
            user=user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Testowa 1',
            emergency_contact_name='Test Contact',
            emergency_contact_phone='123456789',
            diabetes_type='healthy'
        )

    def test_get_masked_pesel(self):
        """Test PESEL masking"""
        masked = self.patient.get_masked_pesel()
        self.assertEqual(masked, '92****52')
        self.assertEqual(len(masked), 8)

    def test_get_masked_emergency_phone(self):
        """Test emergency phone masking"""
        masked = self.patient.get_masked_emergency_phone()
        self.assertEqual(masked, '123***789')
        self.assertEqual(len(masked), 9)

    def test_masked_pesel_for_short_pesel(self):
        """Test masking for invalid short PESEL"""
        self.patient.pesel = '123'
        masked = self.patient.get_masked_pesel()
        self.assertEqual(masked, '***')

    def test_masked_phone_for_short_phone(self):
        """Test masking for short phone number"""
        self.patient.emergency_contact_phone = '12345'
        masked = self.patient.get_masked_emergency_phone()
        self.assertEqual(masked, '***')


class PatientPermissionsTest(TestCase):
    """Test can_be_viewed_by permissions"""

    def setUp(self):
        # Create patient user and profile
        self.patient_user = User.objects.create_user(
            username='patient',
            password='pass',
            user_type='patient'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Testowa 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='healthy'
        )

        # Create doctor user and profile
        self.doctor_user = User.objects.create_user(
            username='doctor',
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

        # Create another patient (unrelated)
        self.other_patient_user = User.objects.create_user(
            username='other_patient',
            password='pass',
            user_type='patient'
        )

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='pass',
            email='admin@example.com'
        )

    def test_patient_can_view_own_profile(self):
        """Test that patient can view their own profile"""
        self.assertTrue(self.patient.can_be_viewed_by(self.patient_user))

    def test_other_patient_cannot_view_profile(self):
        """Test that other patients cannot view profile"""
        self.assertFalse(self.patient.can_be_viewed_by(self.other_patient_user))

    def test_doctor_cannot_view_without_appointment(self):
        """Test that doctor cannot view patient without appointment"""
        self.assertFalse(self.patient.can_be_viewed_by(self.doctor_user))

    def test_doctor_can_view_with_appointment(self):
        """Test that doctor can view patient if they have an appointment"""
        # Create appointment
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Test appointment',
            status='scheduled'
        )

        self.assertTrue(self.patient.can_be_viewed_by(self.doctor_user))

    def test_superuser_can_view_all(self):
        """Test that superuser can view all profiles"""
        self.assertTrue(self.patient.can_be_viewed_by(self.superuser))


class PatientSensitiveFieldsTest(TestCase):
    """Test get_sensitive_fields method"""

    def test_get_sensitive_fields(self):
        """Test that sensitive fields list is correct"""
        user = User.objects.create_user(username='patient', password='pass')
        patient = Patient.objects.create(
            user=user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Testowa 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='healthy'
        )

        sensitive_fields = patient.get_sensitive_fields()

        expected_fields = ['pesel', 'address', 'emergency_contact_phone',
                          'current_medications', 'allergies']

        self.assertEqual(sensitive_fields, expected_fields)


class PatientAppointmentMethodsTest(TestCase):
    """Test appointment-related methods"""

    def setUp(self):
        # Create patient
        self.patient_user = User.objects.create_user(
            username='patient',
            password='pass',
            user_type='patient'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(1992, 3, 21),
            pesel='92032109552',
            address='ul. Testowa 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='healthy'
        )

        # Create doctor
        self.doctor_user = User.objects.create_user(
            username='doctor',
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

    def test_get_total_appointments_zero(self):
        """Test total appointments when patient has no appointments"""
        self.assertEqual(self.patient.get_total_appointments(), 0)

    def test_get_total_appointments(self):
        """Test total appointments count"""
        # Create 3 appointments
        for i in range(3):
            Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                appointment_date=timezone.now() + timedelta(days=i),
                reason=f'Visit {i}',
                status='scheduled'
            )

        self.assertEqual(self.patient.get_total_appointments(), 3)

    def test_get_last_appointment_none(self):
        """Test get_last_appointment when no completed appointments"""
        self.assertIsNone(self.patient.get_last_appointment())

    def test_get_last_appointment(self):
        """Test get_last_appointment returns most recent completed"""
        # Create completed appointments
        apt1 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=10),
            reason='Old visit',
            status='completed'
        )

        apt2 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=5),
            reason='Recent visit',
            status='completed'
        )

        # Create scheduled appointment (should be ignored)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Future visit',
            status='scheduled'
        )

        last = self.patient.get_last_appointment()
        self.assertEqual(last, apt2)
        self.assertEqual(last.reason, 'Recent visit')

    def test_get_next_appointment_none(self):
        """Test get_next_appointment when no scheduled appointments"""
        self.assertIsNone(self.patient.get_next_appointment())

    def test_get_next_appointment(self):
        """Test get_next_appointment returns nearest future appointment"""
        # Create future appointments
        apt1 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=10),
            reason='Far future',
            status='scheduled'
        )

        apt2 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=2),
            reason='Near future',
            status='scheduled'
        )

        # Create past appointment (should be ignored)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=1),
            reason='Past visit',
            status='completed'
        )

        next_apt = self.patient.get_next_appointment()
        self.assertEqual(next_apt, apt2)
        self.assertEqual(next_apt.reason, 'Near future')

    def test_get_next_appointment_ignores_cancelled(self):
        """Test that get_next_appointment ignores cancelled appointments"""
        # Create cancelled appointment
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Cancelled visit',
            status='cancelled'
        )

        self.assertIsNone(self.patient.get_next_appointment())
