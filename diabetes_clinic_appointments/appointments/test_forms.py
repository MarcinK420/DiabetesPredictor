"""
Testy dla formularzy appointments.

Testuje:
- AppointmentBookingForm
- AppointmentEditForm
"""

from datetime import datetime, timedelta, time
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from appointments.forms import AppointmentBookingForm, AppointmentEditForm
from appointments.models import Appointment
from patients.models import Patient
from doctors.models import Doctor

User = get_user_model()


class AppointmentBookingFormTest(TestCase):
    """Testy formularza rezerwacji wizyty"""

    def setUp(self):
        """Przygotowanie danych testowych"""
        # Utwórz pacjenta
        self.patient_user = User.objects.create_user(
            username='patient1',
            password='TestPass123!',
            user_type='patient'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth='1990-01-01',
            pesel='90010100002'  # Valid PESEL for 1990-01-01
        )

        # Utwórz lekarza
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            password='TestPass123!',
            user_type='doctor'
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            license_number='PWZ123',
            specialization='diabetologist',  # Correct value from Doctor model
            is_accepting_patients=True,
            working_hours_start=time(8, 0),
            working_hours_end=time(17, 0),
            years_of_experience=10,
            office_address='Test Office',
            consultation_fee=200.00,
            education='Medical University'
        )

        # Data wizyty: następny poniedziałek o 10:00
        self.next_monday = self.get_next_monday()
        self.valid_appointment_date = timezone.make_aware(
            datetime.combine(self.next_monday, time(10, 0))
        )

        self.valid_data = {
            'doctor': self.doctor.id,
            'appointment_date': self.valid_appointment_date.strftime('%Y-%m-%dT%H:%M'),
            'reason': 'Regular checkup'
        }

    def get_next_monday(self):
        """Zwraca datę następnego poniedziałku"""
        today = timezone.now().date()
        days_ahead = 0 - today.weekday()  # Monday is 0
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days=days_ahead)

    def test_valid_appointment_booking(self):
        """Test poprawnej rezerwacji wizyty"""
        form = AppointmentBookingForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_appointment_date_in_past(self):
        """Test wizyty w przeszłości"""
        past_date = timezone.now() - timedelta(days=1)
        data = self.valid_data.copy()
        data['appointment_date'] = past_date.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentBookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('appointment_date', form.errors)
        self.assertIn('przyszłości', str(form.errors['appointment_date']))

    def test_appointment_date_too_far_future(self):
        """Test wizyty za daleko w przyszłości (>6 miesięcy)"""
        far_future = timezone.now() + timedelta(days=200)
        data = self.valid_data.copy()
        data['appointment_date'] = far_future.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentBookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('appointment_date', form.errors)
        self.assertIn('6 miesięcy', str(form.errors['appointment_date']))

    def test_appointment_on_weekend_saturday(self):
        """Test wizyty w sobotę"""
        # Znajdź następną sobotę
        today = timezone.now().date()
        days_ahead = 5 - today.weekday()  # Saturday is 5
        if days_ahead <= 0:
            days_ahead += 7
        next_saturday = today + timedelta(days=days_ahead)
        saturday_date = timezone.make_aware(
            datetime.combine(next_saturday, time(10, 0))
        )

        data = self.valid_data.copy()
        data['appointment_date'] = saturday_date.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentBookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('poniedziałku do piątku', str(form.errors['__all__']))

    def test_appointment_on_weekend_sunday(self):
        """Test wizyty w niedzielę"""
        # Znajdź następną niedzielę
        today = timezone.now().date()
        days_ahead = 6 - today.weekday()  # Sunday is 6
        if days_ahead <= 0:
            days_ahead += 7
        next_sunday = today + timedelta(days=days_ahead)
        sunday_date = timezone.make_aware(
            datetime.combine(next_sunday, time(10, 0))
        )

        data = self.valid_data.copy()
        data['appointment_date'] = sunday_date.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentBookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('poniedziałku do piątku', str(form.errors['__all__']))

    def test_appointment_before_working_hours(self):
        """Test wizyty przed godzinami pracy (przed 8:00)"""
        early_morning = timezone.make_aware(
            datetime.combine(self.next_monday, time(7, 30))
        )
        data = self.valid_data.copy()
        data['appointment_date'] = early_morning.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentBookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('8:00-17:00', str(form.errors['__all__']))

    def test_appointment_after_working_hours(self):
        """Test wizyty po godzinach pracy (po 17:00)"""
        late_evening = timezone.make_aware(
            datetime.combine(self.next_monday, time(17, 30))
        )
        data = self.valid_data.copy()
        data['appointment_date'] = late_evening.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentBookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('8:00-17:00', str(form.errors['__all__']))

    def test_appointment_at_exact_start_time(self):
        """Test wizyty dokładnie o 8:00"""
        start_time = timezone.make_aware(
            datetime.combine(self.next_monday, time(8, 0))
        )
        data = self.valid_data.copy()
        data['appointment_date'] = start_time.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentBookingForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_appointment_at_exact_end_time(self):
        """Test wizyty dokładnie o 17:00 (nie powinna być dozwolona)"""
        end_time = timezone.make_aware(
            datetime.combine(self.next_monday, time(17, 0))
        )
        data = self.valid_data.copy()
        data['appointment_date'] = end_time.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentBookingForm(data=data)
        # Godzina 17 nie jest dozwolona (hour >= 17)
        self.assertFalse(form.is_valid())

    def test_conflicting_appointment(self):
        """Test konfliktu z istniejącą wizytą"""
        # Utwórz istniejącą wizytę
        existing_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.valid_appointment_date,
            reason='Existing appointment',
            status='scheduled'
        )

        # Spróbuj utworzyć wizytę w tym samym czasie
        form = AppointmentBookingForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('zajęty', str(form.errors['__all__']))

    def test_conflicting_appointment_within_buffer_before(self):
        """Test konfliktu w buforze 15 minut przed"""
        # Istniejąca wizyta o 10:00
        existing_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.valid_appointment_date,
            reason='Existing',
            status='scheduled'
        )

        # Spróbuj umówić wizytę o 9:50 (10 minut przed)
        ten_minutes_before = self.valid_appointment_date - timedelta(minutes=10)
        data = self.valid_data.copy()
        data['appointment_date'] = ten_minutes_before.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentBookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('zajęty', str(form.errors['__all__']))

    def test_conflicting_appointment_within_buffer_after(self):
        """Test konfliktu w buforze 45 minut po"""
        # Istniejąca wizyta o 10:00
        existing_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.valid_appointment_date,
            reason='Existing',
            status='scheduled'
        )

        # Spróbuj umówić wizytę o 10:20 (20 minut po)
        # Range będzie: (10:20 - 15min) do (10:20 + 45min) = 10:05 do 11:05
        # 10:00 (existing) jest poza zakresem (przed 10:05), więc nie będzie konfliktu
        # Zamiast tego, umów o 9:50
        # Range: (9:50 - 15) do (9:50 + 45) = 9:35 do 10:35
        # 10:00 jest w tym zakresie, więc będzie konflikt
        ten_minutes_before = self.valid_appointment_date - timedelta(minutes=10)
        data = self.valid_data.copy()
        data['appointment_date'] = ten_minutes_before.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentBookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('zajęty', str(form.errors['__all__']))

    def test_no_conflict_outside_buffer(self):
        """Test braku konfliktu poza buforem"""
        # Istniejąca wizyta o 10:00
        existing_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.valid_appointment_date,
            reason='Existing',
            status='scheduled'
        )

        # Wizyta o 11:00 (60 minut po, poza buforem 45 min)
        one_hour_after = self.valid_appointment_date + timedelta(hours=1)
        data = self.valid_data.copy()
        data['appointment_date'] = one_hour_after.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentBookingForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_cancelled_appointment_not_conflicting(self):
        """Test że anulowane wizyty nie powodują konfliktu"""
        # Utwórz anulowaną wizytę
        cancelled_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.valid_appointment_date,
            reason='Cancelled',
            status='cancelled'
        )

        form = AppointmentBookingForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_completed_appointment_not_conflicting(self):
        """Test że ukończone wizyty nie powodują konfliktu"""
        # Utwórz ukończoną wizytę
        completed_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.valid_appointment_date,
            reason='Completed',
            status='completed'
        )

        form = AppointmentBookingForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_only_accepting_doctors(self):
        """Test że tylko lekarze przyjmujący pacjentów są dostępni"""
        form = AppointmentBookingForm()

        # Sprawdź że queryset zawiera tylko lekarzy przyjmujących
        doctors_queryset = form.fields['doctor'].queryset
        for doctor in doctors_queryset:
            self.assertTrue(doctor.is_accepting_patients)

    def test_doctor_not_accepting_patients(self):
        """Test że nie można wybrać lekarza nieprzyjmującego pacjentów"""
        # Zmień lekarza na nieprzyjmującego
        self.doctor.is_accepting_patients = False
        self.doctor.save()

        form = AppointmentBookingForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('doctor', form.errors)

    def test_missing_required_fields(self):
        """Test brakujących wymaganych pól"""
        required_fields = ['doctor', 'appointment_date', 'reason']

        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ''

            form = AppointmentBookingForm(data=data)
            self.assertFalse(form.is_valid(), f"Field {field} should be required")
            self.assertIn(field, form.errors, f"Missing error for field {field}")


class AppointmentEditFormTest(TestCase):
    """Testy formularza edycji wizyty"""

    def setUp(self):
        """Przygotowanie danych testowych"""
        # Utwórz pacjenta
        self.patient_user = User.objects.create_user(
            username='patient1',
            password='TestPass123!',
            user_type='patient'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth='1990-01-01',
            pesel='90010100002'  # Valid PESEL for 1990-01-01
        )

        # Utwórz lekarza
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            password='TestPass123!',
            user_type='doctor'
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            license_number='PWZ123',
            specialization='diabetologist',  # Correct value from Doctor model
            is_accepting_patients=True,
            working_hours_start=time(8, 0),
            working_hours_end=time(17, 0),
            years_of_experience=10,
            office_address='Test Office',
            consultation_fee=200.00,
            education='Medical University'
        )

        # Data wizyty: następny poniedziałek o 10:00
        self.next_monday = self.get_next_monday()
        self.valid_appointment_date = timezone.make_aware(
            datetime.combine(self.next_monday, time(10, 0))
        )

        # Utwórz wizytę do edycji
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.valid_appointment_date,
            reason='Original reason',
            status='scheduled'
        )

        # Nowa data (11:00)
        self.new_appointment_date = timezone.make_aware(
            datetime.combine(self.next_monday, time(11, 0))
        )

        self.valid_data = {
            'doctor': self.doctor.id,
            'appointment_date': self.new_appointment_date.strftime('%Y-%m-%dT%H:%M'),
            'reason': 'Updated reason'
        }

    def get_next_monday(self):
        """Zwraca datę następnego poniedziałku"""
        today = timezone.now().date()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days=days_ahead)

    def test_valid_appointment_edit(self):
        """Test poprawnej edycji wizyty"""
        form = AppointmentEditForm(
            data=self.valid_data,
            appointment_id=self.appointment.id
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_edit_excludes_own_id_from_conflicts(self):
        """Test że edycja wykluwa własne ID z konfliktów"""
        # Spróbuj zmienić wizytę na ten sam czas (powinna być OK)
        data = self.valid_data.copy()
        data['appointment_date'] = self.valid_appointment_date.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentEditForm(
            data=data,
            appointment_id=self.appointment.id
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_edit_conflicts_with_other_appointment(self):
        """Test konfliktu z inną wizytą podczas edycji"""
        # Utwórz drugą wizytę o 11:00
        other_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.new_appointment_date,
            reason='Other appointment',
            status='scheduled'
        )

        # Spróbuj zmienić pierwszą wizytę na 11:00
        form = AppointmentEditForm(
            data=self.valid_data,
            appointment_id=self.appointment.id
        )
        self.assertFalse(form.is_valid())
        self.assertIn('zajęty', str(form.errors['__all__']))

    def test_edit_without_appointment_id(self):
        """Test edycji bez podania ID wizyty"""
        # Utwórz drugą wizytę o 11:00
        other_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.new_appointment_date,
            reason='Other appointment',
            status='scheduled'
        )

        # Formularz bez appointment_id
        form = AppointmentEditForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        # Powienien wykryć konflikt bo nie wykluczył żadnego ID

    def test_edit_same_validations_as_booking(self):
        """Test że edycja ma te same walidacje co rezerwacja"""
        # Test przeszłości
        past_date = timezone.now() - timedelta(days=1)
        data = self.valid_data.copy()
        data['appointment_date'] = past_date.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentEditForm(data=data, appointment_id=self.appointment.id)
        self.assertFalse(form.is_valid())
        self.assertIn('przyszłości', str(form.errors['appointment_date']))

    def test_edit_weekend_validation(self):
        """Test walidacji weekendu podczas edycji"""
        # Sobota
        today = timezone.now().date()
        days_ahead = 5 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_saturday = today + timedelta(days=days_ahead)
        saturday_date = timezone.make_aware(
            datetime.combine(next_saturday, time(10, 0))
        )

        data = self.valid_data.copy()
        data['appointment_date'] = saturday_date.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentEditForm(data=data, appointment_id=self.appointment.id)
        self.assertFalse(form.is_valid())
        self.assertIn('poniedziałku do piątku', str(form.errors['__all__']))

    def test_edit_working_hours_validation(self):
        """Test walidacji godzin pracy podczas edycji"""
        # Przed 8:00
        early_morning = timezone.make_aware(
            datetime.combine(self.next_monday, time(7, 0))
        )
        data = self.valid_data.copy()
        data['appointment_date'] = early_morning.strftime('%Y-%m-%dT%H:%M')

        form = AppointmentEditForm(data=data, appointment_id=self.appointment.id)
        self.assertFalse(form.is_valid())
        self.assertIn('8:00-17:00', str(form.errors['__all__']))

    def test_edit_change_doctor(self):
        """Test zmiany lekarza podczas edycji"""
        # Utwórz drugiego lekarza
        doctor2_user = User.objects.create_user(
            username='doctor2',
            password='TestPass123!',
            user_type='doctor'
        )
        doctor2 = Doctor.objects.create(
            user=doctor2_user,
            license_number='PWZ456',
            specialization='endocrinologist',  # Correct value from Doctor model
            is_accepting_patients=True,
            working_hours_start=time(8, 0),
            working_hours_end=time(17, 0),
            years_of_experience=15,
            office_address='Test Office 2',
            consultation_fee=250.00,
            education='Medical University 2'
        )

        data = self.valid_data.copy()
        data['doctor'] = doctor2.id

        form = AppointmentEditForm(data=data, appointment_id=self.appointment.id)
        self.assertTrue(form.is_valid(), form.errors)

    def test_edit_change_reason(self):
        """Test zmiany powodu wizyty"""
        data = self.valid_data.copy()
        data['reason'] = 'Completely new reason for the visit'

        form = AppointmentEditForm(data=data, appointment_id=self.appointment.id)
        self.assertTrue(form.is_valid(), form.errors)
