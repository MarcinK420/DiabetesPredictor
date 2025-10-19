"""
Integration tests for doctors views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta, time
from authentication.models import User
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment


class DoctorDashboardViewTest(TestCase):
    """Test dashboard view for doctors"""

    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('doctors:dashboard')

        # Create doctor user
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
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        # Create patient
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
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='type1'
        )

    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_dashboard_accessible_for_doctor(self):
        """Test dashboard is accessible for logged-in doctor"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doctors/dashboard.html')
        self.assertIn('doctor', response.context)
        self.assertEqual(response.context['doctor'], self.doctor)

    def test_dashboard_redirects_patient(self):
        """Test dashboard redirects patient users"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.dashboard_url)

        self.assertRedirects(response, reverse('authentication:login'))

    def test_dashboard_shows_statistics(self):
        """Test dashboard displays appointment statistics"""
        self.client.login(username='doctor_test', password='testpass123')

        # Create appointments for today
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now(),
            reason='Today visit',
            status='scheduled'
        )

        # Create appointments for next week
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=3),
            reason='Future visit',
            status='scheduled'
        )

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.context['today_appointments'], 1)
        self.assertGreaterEqual(response.context['upcoming_appointments'], 1)
        self.assertEqual(response.context['total_patients'], 1)
        self.assertIsNotNone(response.context['next_appointment'])

    def test_dashboard_counts_unique_patients(self):
        """Test dashboard counts unique patients correctly"""
        self.client.login(username='doctor_test', password='testpass123')

        # Create multiple appointments with same patient
        for i in range(3):
            Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                appointment_date=timezone.now() + timedelta(days=i),
                reason=f'Visit {i}',
                status='scheduled'
            )

        response = self.client.get(self.dashboard_url)

        # Should count 1 unique patient, not 3
        self.assertEqual(response.context['total_patients'], 1)


class DoctorUpcomingAppointmentsViewTest(TestCase):
    """Test upcoming_appointments view for doctors"""

    def setUp(self):
        self.client = Client()
        self.upcoming_url = reverse('doctors:upcoming_appointments')

        # Create doctor
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
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        # Create patient
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
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='type1'
        )

    def test_upcoming_appointments_requires_login(self):
        """Test view requires authentication"""
        response = self.client.get(self.upcoming_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_upcoming_appointments_accessible_for_doctor(self):
        """Test view is accessible for logged-in doctor"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.upcoming_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doctors/upcoming_appointments.html')

    def test_upcoming_appointments_shows_only_future(self):
        """Test view shows only future scheduled appointments"""
        self.client.login(username='doctor_test', password='testpass123')

        # Create past appointment (should not appear)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=1),
            reason='Past visit',
            status='completed'
        )

        # Create future appointment (should appear)
        future_apt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            reason='Future visit',
            status='scheduled'
        )

        response = self.client.get(self.upcoming_url)

        # Check appointments are grouped by date
        self.assertIn('appointments_by_date', response.context)
        self.assertIn('today_appointments', response.context)
        self.assertGreaterEqual(response.context['total_upcoming'], 1)

    def test_upcoming_appointments_groups_by_date(self):
        """Test appointments are grouped by date"""
        self.client.login(username='doctor_test', password='testpass123')

        # Create appointments on different dates
        date1 = timezone.now() + timedelta(days=1)
        date2 = timezone.now() + timedelta(days=2)

        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date1,
            reason='Visit day 1',
            status='scheduled'
        )
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date2,
            reason='Visit day 2',
            status='scheduled'
        )

        response = self.client.get(self.upcoming_url)

        appointments_by_date = response.context['appointments_by_date']
        self.assertGreaterEqual(len(appointments_by_date), 2)


class DoctorPatientsListViewTest(TestCase):
    """Test patients_list view for doctors"""

    def setUp(self):
        self.client = Client()
        self.patients_list_url = reverse('doctors:patients_list')

        # Create doctor
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
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        # Create patients
        self.patients = []
        for i in range(15):  # Create 15 patients for pagination test
            patient_user = User.objects.create_user(
                username=f'patient_{i}',
                password='testpass123',
                user_type='patient',
                first_name=f'Patient{i}',
                last_name=f'Test{i}'
            )
            patient = Patient.objects.create(
                user=patient_user,
                date_of_birth=date(1990, 1, 1),
                pesel=f'9001010000{i}',
                address='ul. Test 1',
                emergency_contact_name='Test',
                emergency_contact_phone='123',
                diabetes_type='type1'
            )
            self.patients.append(patient)

            # Create appointment with doctor
            Appointment.objects.create(
                patient=patient,
                doctor=self.doctor,
                appointment_date=timezone.now() + timedelta(days=i),
                reason='Test visit',
                status='scheduled'
            )

    def test_patients_list_requires_login(self):
        """Test view requires authentication"""
        response = self.client.get(self.patients_list_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_patients_list_accessible_for_doctor(self):
        """Test view is accessible for logged-in doctor"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.patients_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doctors/patients_list.html')

    def test_patients_list_pagination(self):
        """Test patients list is paginated (10 per page)"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.patients_list_url)

        # Should have pagination
        self.assertIn('page_obj', response.context)
        page_obj = response.context['page_obj']

        # First page should have 10 patients
        self.assertEqual(len(page_obj), 10)
        self.assertTrue(page_obj.has_next())

        # Get second page
        response = self.client.get(self.patients_list_url + '?page=2')
        page_obj = response.context['page_obj']

        # Second page should have remaining 5 patients
        self.assertEqual(len(page_obj), 5)
        self.assertFalse(page_obj.has_next())

    def test_patients_list_shows_statistics(self):
        """Test patients list shows appointment statistics"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.patients_list_url)

        self.assertEqual(response.context['total_patients'], 15)
        self.assertIn('patients_with_scheduled', response.context)


class DoctorPatientDetailViewTest(TestCase):
    """Test patient_detail view for doctors"""

    def setUp(self):
        self.client = Client()

        # Create doctor
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
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        # Create patient with appointments
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
            emergency_contact_name='Test',
            emergency_contact_phone='123',
            diabetes_type='type1'
        )

        # Create patient without appointments (no access)
        self.other_patient_user = User.objects.create_user(
            username='other_patient',
            password='testpass123',
            user_type='patient'
        )
        self.other_patient = Patient.objects.create(
            user=self.other_patient_user,
            date_of_birth=date(1990, 1, 1),
            pesel='90010112345',
            address='ul. Other 1',
            emergency_contact_name='Other',
            emergency_contact_phone='456',
            diabetes_type='type2'
        )

        # Create appointments with patient
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=10),
            reason='Past visit',
            status='completed'
        )

        self.patient_detail_url = reverse('doctors:patient_detail', kwargs={'patient_id': self.patient.id})

    def test_patient_detail_requires_login(self):
        """Test view requires authentication"""
        response = self.client.get(self.patient_detail_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_patient_detail_accessible_with_permission(self):
        """Test view is accessible when doctor has appointments with patient"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.patient_detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doctors/patient_detail.html')
        self.assertEqual(response.context['patient'], self.patient)

    def test_patient_detail_denies_access_without_appointments(self):
        """Test view returns 404 when doctor has no appointments with patient"""
        self.client.login(username='doctor_test', password='testpass123')

        # Try to access patient without appointments
        other_patient_url = reverse('doctors:patient_detail', kwargs={'patient_id': self.other_patient.id})
        response = self.client.get(other_patient_url)

        self.assertEqual(response.status_code, 404)

    def test_patient_detail_shows_appointment_history(self):
        """Test view shows appointment history"""
        self.client.login(username='doctor_test', password='testpass123')

        # Create more appointments
        for i in range(15):  # Create 15 appointments for pagination
            Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                appointment_date=timezone.now() - timedelta(days=i+1),
                reason=f'Visit {i}',
                status='completed'
            )

        response = self.client.get(self.patient_detail_url)

        # Check pagination (10 appointments per page)
        self.assertIn('page_obj', response.context)
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 10)

    def test_patient_detail_shows_statistics(self):
        """Test view shows appointment statistics"""
        self.client.login(username='doctor_test', password='testpass123')

        # Create various appointment statuses
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=5),
            reason='Future visit',
            status='scheduled'
        )
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=1),
            reason='Cancelled visit',
            status='cancelled'
        )

        response = self.client.get(self.patient_detail_url)

        # Check statistics are present
        self.assertIn('total_appointments', response.context)
        self.assertIn('completed_appointments', response.context)
        self.assertIn('cancelled_appointments', response.context)
        self.assertIn('scheduled_appointments', response.context)
        self.assertGreaterEqual(response.context['total_appointments'], 3)
