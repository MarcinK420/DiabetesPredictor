"""
Integration tests for appointments views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import date, timedelta, time
from authentication.models import User
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment


class PatientAppointmentHistoryViewTest(TestCase):
    """Test patient_appointment_history view"""

    def setUp(self):
        self.client = Client()
        self.history_url = reverse('appointments:patient_history')

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
            education='Medical University',
            is_accepting_patients=True
        )

    def test_history_requires_login(self):
        """Test history view requires authentication"""
        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_history_accessible_for_patient(self):
        """Test history is accessible for logged-in patient"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointments/patient_history.html')
        self.assertIn('appointments', response.context)

    def test_history_redirects_doctor(self):
        """Test history redirects doctor users"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.history_url)

        self.assertRedirects(response, reverse('authentication:login'))

    def test_history_shows_all_appointments(self):
        """Test history shows all appointments (past and future)"""
        self.client.login(username='patient_test', password='testpass123')

        # Create past appointment
        past_apt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=10),
            reason='Past visit',
            status='completed'
        )

        # Create future appointment
        future_apt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=10),
            reason='Future visit',
            status='scheduled'
        )

        response = self.client.get(self.history_url)
        appointments = response.context['appointments']

        self.assertEqual(len(appointments), 2)

    def test_history_pagination(self):
        """Test history is paginated (10 per page)"""
        self.client.login(username='patient_test', password='testpass123')

        # Create 15 appointments
        for i in range(15):
            Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                appointment_date=timezone.now() + timedelta(days=i),
                reason=f'Visit {i}',
                status='scheduled'
            )

        response = self.client.get(self.history_url)
        page_obj = response.context['appointments']

        # First page should have 10 appointments
        self.assertEqual(len(page_obj), 10)
        self.assertTrue(page_obj.has_next())

        # Get second page
        response = self.client.get(self.history_url + '?page=2')
        page_obj = response.context['appointments']

        # Second page should have remaining 5
        self.assertEqual(len(page_obj), 5)
        self.assertFalse(page_obj.has_next())


class AppointmentDetailViewTest(TestCase):
    """Test appointment_detail view"""

    def setUp(self):
        self.client = Client()

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

        # Create another patient
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
            education='Medical University',
            is_accepting_patients=True
        )

        # Create appointment for patient
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=5),
            reason='Test visit',
            status='scheduled'
        )

        self.detail_url = reverse('appointments:detail', kwargs={'appointment_id': self.appointment.id})

    def test_detail_requires_login(self):
        """Test detail view requires authentication"""
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_detail_accessible_for_owner(self):
        """Test detail is accessible for appointment owner"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointments/appointment_detail.html')
        self.assertEqual(response.context['appointment'], self.appointment)

    def test_detail_denies_access_to_other_patient(self):
        """Test detail returns 404 for other patients"""
        self.client.login(username='other_patient', password='testpass123')
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 404)

    def test_detail_redirects_doctor(self):
        """Test detail redirects doctor users"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.detail_url)

        self.assertRedirects(response, reverse('authentication:login'))


class BookAppointmentViewTest(TestCase):
    """Test book_appointment view (FR-06)"""

    def setUp(self):
        self.client = Client()
        self.book_url = reverse('appointments:book_appointment')

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
            education='Medical University',
            is_accepting_patients=True
        )

    def test_book_requires_login(self):
        """Test booking view requires authentication"""
        response = self.client.get(self.book_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_book_accessible_for_patient(self):
        """Test booking is accessible for logged-in patient"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.book_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointments/book_appointment.html')
        self.assertIn('form', response.context)

    def test_book_redirects_doctor(self):
        """Test booking redirects doctor users"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.book_url)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Tylko pacjenci' in str(m) for m in messages))
        self.assertRedirects(response, reverse('authentication:login'))

    def test_successful_booking(self):
        """Test successful appointment booking"""
        self.client.login(username='patient_test', password='testpass123')

        # Create a valid appointment date (next Monday at 10:00)
        now = timezone.now()
        days_ahead = (7 - now.weekday()) % 7  # Days until next Monday
        if days_ahead == 0:
            days_ahead = 7  # If today is Monday, use next Monday
        future_date = now + timedelta(days=days_ahead)
        # Set time to 10:00
        future_date = future_date.replace(hour=10, minute=0, second=0, microsecond=0)

        response = self.client.post(self.book_url, {
            'doctor': self.doctor.id,
            'appointment_date': future_date.strftime('%Y-%m-%dT%H:%M'),
            'reason': 'Regular checkup',
        })

        self.assertRedirects(response, reverse('appointments:patient_history'))

        # Verify appointment was created
        appointment = Appointment.objects.filter(patient=self.patient).first()
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.reason, 'Regular checkup')

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Pomyślnie zapisano' in str(m) for m in messages))

    def test_booking_blocked_during_cooldown(self):
        """Test booking is blocked during 2-minute cooldown after cancellation"""
        self.client.login(username='patient_test', password='testpass123')

        # Set recent cancellation
        self.patient.last_cancellation_time = timezone.now()
        self.patient.save()

        response = self.client.get(self.book_url)

        # Should be blocked
        self.assertRedirects(response, reverse('appointments:upcoming'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('odczekać' in str(m) for m in messages))

    def test_booking_allowed_after_cooldown(self):
        """Test booking is allowed after cooldown expires"""
        self.client.login(username='patient_test', password='testpass123')

        # Set old cancellation (more than 2 minutes ago)
        self.patient.last_cancellation_time = timezone.now() - timedelta(minutes=3)
        self.patient.save()

        response = self.client.get(self.book_url)

        # Should be allowed
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_cooldown_info_in_context(self):
        """Test cooldown info is provided in context during cooldown"""
        self.client.login(username='patient_test', password='testpass123')

        # Set recent cancellation
        self.patient.last_cancellation_time = timezone.now() - timedelta(seconds=30)
        self.patient.save()

        # This should redirect, so we need to follow=False
        response = self.client.get(self.book_url)

        # Verify redirect happened
        self.assertEqual(response.status_code, 302)


class UpcomingAppointmentsViewTest(TestCase):
    """Test upcoming_appointments view"""

    def setUp(self):
        self.client = Client()
        self.upcoming_url = reverse('appointments:upcoming')

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
            education='Medical University',
            is_accepting_patients=True
        )

    def test_upcoming_requires_login(self):
        """Test upcoming view requires authentication"""
        response = self.client.get(self.upcoming_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_upcoming_accessible_for_patient(self):
        """Test upcoming is accessible for logged-in patient"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.upcoming_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointments/upcoming_appointments.html')
        self.assertIn('appointments', response.context)

    def test_upcoming_redirects_doctor(self):
        """Test upcoming redirects doctor users"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.upcoming_url)

        self.assertRedirects(response, reverse('authentication:login'))

    def test_upcoming_shows_only_future_scheduled(self):
        """Test upcoming shows only future scheduled appointments"""
        self.client.login(username='patient_test', password='testpass123')

        # Create past appointment (should not appear)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=5),
            reason='Past visit',
            status='completed'
        )

        # Create future scheduled appointment (should appear)
        future_apt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=5),
            reason='Future visit',
            status='scheduled'
        )

        # Create future cancelled appointment (should not appear)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=7),
            reason='Cancelled visit',
            status='cancelled'
        )

        response = self.client.get(self.upcoming_url)
        appointments = response.context['appointments']

        self.assertEqual(len(appointments), 1)
        self.assertEqual(appointments[0], future_apt)


class EditAppointmentViewTest(TestCase):
    """Test edit_appointment view (FR-07)"""

    def setUp(self):
        self.client = Client()

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
            education='Medical University',
            is_accepting_patients=True
        )

        # Create future appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=7),
            reason='Original reason',
            status='scheduled'
        )

        self.edit_url = reverse('appointments:edit_appointment', kwargs={'appointment_id': self.appointment.id})

    def test_edit_requires_login(self):
        """Test edit view requires authentication"""
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_edit_accessible_for_owner(self):
        """Test edit is accessible for appointment owner"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointments/edit_appointment.html')
        self.assertIn('form', response.context)

    def test_edit_redirects_doctor(self):
        """Test edit redirects doctor users"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.edit_url)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Tylko pacjenci' in str(m) for m in messages))
        self.assertRedirects(response, reverse('authentication:login'))

    def test_successful_edit(self):
        """Test successful appointment edit"""
        self.client.login(username='patient_test', password='testpass123')

        new_date = timezone.now() + timedelta(days=10)
        response = self.client.post(self.edit_url, {
            'doctor': self.doctor.id,
            'appointment_date': new_date.strftime('%Y-%m-%d %H:%M'),
            'reason': 'Updated reason',
        })

        self.assertRedirects(response, reverse('appointments:upcoming'))

        # Verify changes were saved
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.reason, 'Updated reason')

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Zapisano zmiany' in str(m) for m in messages))

    def test_cannot_edit_past_appointment(self):
        """Test cannot edit appointment in the past"""
        self.client.login(username='patient_test', password='testpass123')

        # Create past appointment
        past_apt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=1),
            reason='Past visit',
            status='scheduled'
        )

        edit_url = reverse('appointments:edit_appointment', kwargs={'appointment_id': past_apt.id})
        response = self.client.get(edit_url)

        self.assertRedirects(response, reverse('appointments:upcoming'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('przeszłości' in str(m) for m in messages))

    def test_cannot_edit_completed_appointment(self):
        """Test cannot edit completed appointment"""
        self.client.login(username='patient_test', password='testpass123')

        # Create completed appointment
        completed_apt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=5),
            reason='Completed visit',
            status='completed'
        )

        edit_url = reverse('appointments:edit_appointment', kwargs={'appointment_id': completed_apt.id})
        response = self.client.get(edit_url)

        # Should get 404 because we filter by status='scheduled'
        self.assertEqual(response.status_code, 404)


class CancelAppointmentViewTest(TestCase):
    """Test cancel_appointment view (FR-08)"""

    def setUp(self):
        self.client = Client()

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
            education='Medical University',
            is_accepting_patients=True
        )

        # Create future appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=7),
            reason='Test visit',
            status='scheduled'
        )

        self.cancel_url = reverse('appointments:cancel_appointment', kwargs={'appointment_id': self.appointment.id})

    def test_cancel_requires_login(self):
        """Test cancel view requires authentication"""
        response = self.client.get(self.cancel_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_cancel_shows_confirmation_page(self):
        """Test GET request shows confirmation page"""
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(self.cancel_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointments/cancel_appointment.html')
        self.assertEqual(response.context['appointment'], self.appointment)

    def test_cancel_redirects_doctor(self):
        """Test cancel redirects doctor users"""
        self.client.login(username='doctor_test', password='testpass123')
        response = self.client.get(self.cancel_url)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Tylko pacjenci' in str(m) for m in messages))
        self.assertRedirects(response, reverse('authentication:login'))

    def test_successful_cancellation(self):
        """Test successful appointment cancellation"""
        self.client.login(username='patient_test', password='testpass123')

        response = self.client.post(self.cancel_url, {
            'confirm_cancellation': 'yes'
        })

        self.assertRedirects(response, reverse('appointments:upcoming'))

        # Verify appointment was cancelled
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'cancelled')

        # Verify cooldown was set
        self.patient.refresh_from_db()
        self.assertIsNotNone(self.patient.last_cancellation_time)

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('odwołano' in str(m) for m in messages))

    def test_cancellation_aborted(self):
        """Test cancellation can be aborted"""
        self.client.login(username='patient_test', password='testpass123')

        response = self.client.post(self.cancel_url, {
            'confirm_cancellation': 'no'
        })

        self.assertRedirects(response, reverse('appointments:upcoming'))

        # Verify appointment was NOT cancelled
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'scheduled')

        # Verify info message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('przerwane' in str(m) for m in messages))

    def test_cannot_cancel_past_appointment(self):
        """Test cannot cancel appointment in the past"""
        self.client.login(username='patient_test', password='testpass123')

        # Create past appointment
        past_apt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() - timedelta(days=1),
            reason='Past visit',
            status='scheduled'
        )

        cancel_url = reverse('appointments:cancel_appointment', kwargs={'appointment_id': past_apt.id})
        response = self.client.get(cancel_url)

        self.assertRedirects(response, reverse('appointments:upcoming'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('przeszłości' in str(m) for m in messages))

    def test_cannot_cancel_completed_appointment(self):
        """Test cannot cancel completed appointment"""
        self.client.login(username='patient_test', password='testpass123')

        # Create completed appointment
        completed_apt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=5),
            reason='Completed visit',
            status='completed'
        )

        cancel_url = reverse('appointments:cancel_appointment', kwargs={'appointment_id': completed_apt.id})
        response = self.client.get(cancel_url)

        # Should get 404 because we filter by status='scheduled'
        self.assertEqual(response.status_code, 404)

    def test_cooldown_prevents_immediate_rebooking(self):
        """Test that cancelling sets cooldown that prevents immediate rebooking"""
        self.client.login(username='patient_test', password='testpass123')

        # Cancel appointment
        self.client.post(self.cancel_url, {
            'confirm_cancellation': 'yes'
        })

        # Try to book new appointment immediately
        book_url = reverse('appointments:book_appointment')
        response = self.client.get(book_url)

        # Should be blocked
        self.assertRedirects(response, reverse('appointments:upcoming'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('odczekać' in str(m) for m in messages))
