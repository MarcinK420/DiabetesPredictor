"""
Tests for Appointment model.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from authentication.models import User
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment


class AppointmentCreationTest(TestCase):
    """Test Appointment model creation"""

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
            address='ul. Test 1',
            emergency_contact_name='Emergency Contact',
            emergency_contact_phone='123456789',
            diabetes_type='type1'
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

    def test_create_appointment(self):
        """Test creating an appointment"""
        appointment_time = timezone.now() + timedelta(days=1)

        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=appointment_time,
            reason='Regular checkup',
            status='scheduled'
        )

        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.reason, 'Regular checkup')
        self.assertEqual(appointment.status, 'scheduled')
        self.assertEqual(appointment.duration_minutes, 30)  # Default

    def test_default_status(self):
        """Test that default status is 'scheduled'"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Test visit'
        )

        self.assertEqual(appointment.status, 'scheduled')

    def test_default_duration(self):
        """Test that default duration is 30 minutes"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Test visit'
        )

        self.assertEqual(appointment.duration_minutes, 30)

    def test_custom_duration(self):
        """Test setting custom duration"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Extended consultation',
            duration_minutes=60
        )

        self.assertEqual(appointment.duration_minutes, 60)


class AppointmentStrMethodTest(TestCase):
    """Test Appointment __str__ method"""

    def setUp(self):
        # Create patient
        self.patient_user = User.objects.create_user(
            username='patient',
            password='pass',
            user_type='patient',
            first_name='Jan',
            last_name='Kowalski'
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

        # Create doctor
        self.doctor_user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor',
            first_name='Anna',
            last_name='Nowak'
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

    def test_appointment_str_representation(self):
        """Test string representation of appointment"""
        appointment_time = timezone.datetime(2024, 6, 15, 10, 30, tzinfo=timezone.get_current_timezone())

        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=appointment_time,
            reason='Test visit',
            status='scheduled'
        )

        expected_str = 'Jan Kowalski - 2024-06-15 10:30 - Dr. Nowak'
        self.assertEqual(str(appointment), expected_str)


class AppointmentStatusTest(TestCase):
    """Test appointment status choices"""

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
            address='ul. Test 1',
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

    def test_scheduled_status(self):
        """Test scheduled status"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Test',
            status='scheduled'
        )

        self.assertEqual(appointment.status, 'scheduled')
        self.assertEqual(appointment.get_status_display(), 'Zaplanowana')

    def test_completed_status(self):
        """Test completed status"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=1),
            reason='Test',
            status='completed'
        )

        self.assertEqual(appointment.status, 'completed')
        self.assertEqual(appointment.get_status_display(), 'Zakończona')

    def test_cancelled_status(self):
        """Test cancelled status"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Test',
            status='cancelled'
        )

        self.assertEqual(appointment.status, 'cancelled')
        self.assertEqual(appointment.get_status_display(), 'Anulowana')

    def test_no_show_status(self):
        """Test no_show status"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=1),
            reason='Test',
            status='no_show'
        )

        self.assertEqual(appointment.status, 'no_show')
        self.assertEqual(appointment.get_status_display(), 'Niestawiennictwo')


class AppointmentOrderingTest(TestCase):
    """Test appointment ordering (descending by date)"""

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
            address='ul. Test 1',
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

    def test_appointments_ordered_by_date_descending(self):
        """Test that appointments are ordered by date (newest first)"""
        # Create appointments in random order
        apt2 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=2),
            reason='Future appointment 2',
            status='scheduled'
        )

        apt1 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Future appointment 1',
            status='scheduled'
        )

        apt3 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=3),
            reason='Future appointment 3',
            status='scheduled'
        )

        # Get all appointments
        appointments = Appointment.objects.all()

        # Should be ordered: apt3, apt2, apt1 (newest to oldest)
        self.assertEqual(list(appointments), [apt3, apt2, apt1])


class AppointmentRelationshipsTest(TestCase):
    """Test foreign key relationships"""

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
            address='ul. Test 1',
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

    def test_patient_appointments_relationship(self):
        """Test accessing appointments from patient"""
        # Create appointments
        apt1 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Visit 1',
            status='scheduled'
        )

        apt2 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=2),
            reason='Visit 2',
            status='scheduled'
        )

        # Access appointments from patient
        patient_appointments = self.patient.appointments.all()

        self.assertEqual(patient_appointments.count(), 2)
        self.assertIn(apt1, patient_appointments)
        self.assertIn(apt2, patient_appointments)

    def test_doctor_appointments_relationship(self):
        """Test accessing appointments from doctor"""
        # Create appointments
        apt1 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Visit 1',
            status='scheduled'
        )

        apt2 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=2),
            reason='Visit 2',
            status='scheduled'
        )

        # Access appointments from doctor
        doctor_appointments = self.doctor.appointments.all()

        self.assertEqual(doctor_appointments.count(), 2)
        self.assertIn(apt1, doctor_appointments)
        self.assertIn(apt2, doctor_appointments)


class AppointmentNotesTest(TestCase):
    """Test appointment notes field"""

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
            address='ul. Test 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='type1'
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

    def test_notes_optional(self):
        """Test that notes field is optional"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Test visit'
        )

        self.assertEqual(appointment.notes, '')

    def test_notes_can_be_added(self):
        """Test adding notes to appointment"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Test visit',
            notes='Patient shows good glucose control. Continue current medication.'
        )

        self.assertEqual(
            appointment.notes,
            'Patient shows good glucose control. Continue current medication.'
        )

    def test_notes_can_be_updated(self):
        """Test updating notes after appointment"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Test visit',
            status='scheduled'
        )

        # Complete appointment and add notes
        appointment.status = 'completed'
        appointment.notes = 'Appointment completed successfully. Patient healthy.'
        appointment.save()

        appointment.refresh_from_db()

        self.assertEqual(appointment.status, 'completed')
        self.assertEqual(
            appointment.notes,
            'Appointment completed successfully. Patient healthy.'
        )


class AppointmentTimestampsTest(TestCase):
    """Test created_at and updated_at timestamps"""

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
            address='ul. Test 1',
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

    def test_created_at_set_automatically(self):
        """Test that created_at is set automatically"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Test visit'
        )

        self.assertIsNotNone(appointment.created_at)

    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when model is saved"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Test visit',
            status='scheduled'
        )

        original_updated_at = appointment.updated_at

        # Update appointment
        appointment.status = 'completed'
        appointment.save()

        appointment.refresh_from_db()

        self.assertGreaterEqual(appointment.updated_at, original_updated_at)


class AppointmentReasonTest(TestCase):
    """Test reason field"""

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
            address='ul. Test 1',
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='type1'
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

    def test_various_appointment_reasons(self):
        """Test different appointment reasons"""
        reasons = [
            'Regular checkup',
            'Follow-up appointment',
            'New patient consultation',
            'Medication adjustment',
            'Blood sugar monitoring',
            'Diabetes management consultation'
        ]

        for i, reason in enumerate(reasons):
            appointment = Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                appointment_date=timezone.now() + timedelta(days=i+1),
                reason=reason,
                status='scheduled'
            )

            self.assertEqual(appointment.reason, reason)
