from django.db import models
from django.conf import settings
from patients.models import Patient
from doctors.models import Doctor
from ckeditor.fields import RichTextField

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Zaplanowana'),
        ('completed', 'Zakończona'),
        ('cancelled', 'Anulowana'),
        ('no_show', 'Niestawiennictwo'),
    ]

    RECURRENCE_CHOICES = [
        ('none', 'Brak powtórzeń'),
        ('weekly', 'Co tydzień'),
        ('biweekly', 'Co 2 tygodnie'),
        ('monthly', 'Co miesiąc'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    reason = models.CharField(max_length=200, help_text="Powód wizyty")
    notes = RichTextField(blank=True, null=True, config_name='doctor_notes', help_text="Notatki z wizyty (dla lekarza)")
    duration_minutes = models.PositiveIntegerField(default=30)

    # Recurring appointment fields
    is_recurring = models.BooleanField(default=False, help_text="Czy wizyta jest częścią serii")
    recurrence_pattern = models.CharField(
        max_length=15,
        choices=RECURRENCE_CHOICES,
        default='none',
        help_text="Wzorzec powtarzania"
    )
    recurrence_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Data końca powtarzania serii"
    )
    parent_appointment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recurring_instances',
        help_text="Pierwsza wizyta w serii (dla śledzenia całej serii)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date']
        verbose_name = "Wizyta"
        verbose_name_plural = "Wizyty"

    def __str__(self):
        return f"{self.patient.user.first_name} {self.patient.user.last_name} - {self.appointment_date.strftime('%Y-%m-%d %H:%M')} - Dr. {self.doctor.user.last_name}"

    def get_series_appointments(self):
        """Zwraca wszystkie wizyty w serii (włączając tę wizytę)"""
        if self.parent_appointment:
            # To jest jedna z wizyt w serii, zwróć wszystkie z tej samej serii
            return Appointment.objects.filter(
                models.Q(parent_appointment=self.parent_appointment) |
                models.Q(id=self.parent_appointment.id)
            ).order_by('appointment_date')
        elif self.is_recurring:
            # To jest pierwsza wizyta w serii, zwróć ją i wszystkie jej instancje
            return Appointment.objects.filter(
                models.Q(parent_appointment=self) |
                models.Q(id=self.id)
            ).order_by('appointment_date')
        else:
            # To jest pojedyncza wizyta
            return Appointment.objects.filter(id=self.id)
