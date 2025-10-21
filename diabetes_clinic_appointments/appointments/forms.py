from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment
from doctors.models import Doctor


class DateTimePickerWidget(forms.DateTimeInput):
    """Custom widget dla wizualnego kalendarza z Flatpickr"""

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control flatpickr-input',
            'placeholder': 'Wybierz datę i godzinę...',
            'readonly': 'readonly',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format='%Y-%m-%d %H:%M')


class AppointmentBookingForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_accepting_patients=True),
        empty_label="Wybierz lekarza",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Lekarz'
    )

    appointment_date = forms.DateTimeField(
        widget=DateTimePickerWidget(),
        label='Data i godzina wizyty',
        input_formats=['%Y-%m-%d %H:%M']
    )

    reason = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Powód wizyty',
        help_text='Opisz krótko powód wizyty'
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize doctor display to show name and specialization
        self.fields['doctor'].queryset = Doctor.objects.filter(is_accepting_patients=True)

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data['appointment_date']

        # Check if appointment is in the future
        if appointment_date <= timezone.now():
            raise ValidationError('Data wizyty musi być w przyszłości.')

        # Check if appointment is not too far in the future (max 6 months)
        max_date = timezone.now() + timedelta(days=180)
        if appointment_date > max_date:
            raise ValidationError('Nie można umówić wizyty więcej niż 6 miesięcy w przyszłość.')

        return appointment_date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')

        if doctor and appointment_date:
            # Check if doctor has conflicting appointments (within 30 minutes)
            start_time = appointment_date - timedelta(minutes=15)
            end_time = appointment_date + timedelta(minutes=45)  # 30 min appointment + 15 min buffer

            conflicting_appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date__range=(start_time, end_time),
                status__in=['scheduled']
            )

            if conflicting_appointments.exists():
                raise ValidationError('Wybrany termin jest już zajęty. Wybierz inną godzinę.')

            # Basic validation for working hours (assuming 8:00-17:00)
            appointment_hour = appointment_date.hour
            if appointment_hour < 8 or appointment_hour >= 17:
                raise ValidationError('Wizyty można umawiać tylko w godzinach 8:00-17:00.')

            # Check if it's a working day (Monday to Friday)
            if appointment_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                raise ValidationError('Wizyty można umawiać tylko od poniedziałku do piątku.')

        return cleaned_data


class AppointmentEditForm(forms.ModelForm):
    """Formularz edycji wizyty (FR-07)"""

    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_accepting_patients=True),
        empty_label="Wybierz lekarza",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Lekarz'
    )

    appointment_date = forms.DateTimeField(
        widget=DateTimePickerWidget(),
        label='Data i godzina wizyty',
        input_formats=['%Y-%m-%d %H:%M']
    )

    reason = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Powód wizyty',
        help_text='Opisz krótko powód wizyty'
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'reason']

    def __init__(self, *args, **kwargs):
        self.appointment_id = kwargs.pop('appointment_id', None)
        super().__init__(*args, **kwargs)
        # Customize doctor display to show name and specialization
        self.fields['doctor'].queryset = Doctor.objects.filter(is_accepting_patients=True)

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data['appointment_date']

        # Check if appointment is in the future
        if appointment_date <= timezone.now():
            raise ValidationError('Data wizyty musi być w przyszłości.')

        # Check if appointment is not too far in the future (max 6 months)
        max_date = timezone.now() + timedelta(days=180)
        if appointment_date > max_date:
            raise ValidationError('Nie można umówić wizyty więcej niż 6 miesięcy w przyszłość.')

        return appointment_date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')

        if doctor and appointment_date:
            # Check if doctor has conflicting appointments (within 30 minutes)
            # Exclude the current appointment being edited
            start_time = appointment_date - timedelta(minutes=15)
            end_time = appointment_date + timedelta(minutes=45)  # 30 min appointment + 15 min buffer

            conflicting_appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date__range=(start_time, end_time),
                status__in=['scheduled']
            )

            # Exclude current appointment from conflict check
            if self.appointment_id:
                conflicting_appointments = conflicting_appointments.exclude(id=self.appointment_id)

            if conflicting_appointments.exists():
                raise ValidationError('Wybrany termin jest już zajęty. Wybierz inną godzinę.')

            # Basic validation for working hours (assuming 8:00-17:00)
            appointment_hour = appointment_date.hour
            if appointment_hour < 8 or appointment_hour >= 17:
                raise ValidationError('Wizyty można umawiać tylko w godzinach 8:00-17:00.')

            # Check if it's a working day (Monday to Friday)
            if appointment_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                raise ValidationError('Wizyty można umawiać tylko od poniedziałku do piątku.')

        return cleaned_data