from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField()
    pesel = models.CharField(max_length=11, unique=True)
    address = models.TextField()
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    
    diabetes_type = models.CharField(
        max_length=15,
        choices=[
            ('type1', 'Cukrzyca typu 1'),
            ('type2', 'Cukrzyca typu 2'),
            ('gestational', 'Cukrzyca ciążowa'),
        ]
    )
    diagnosis_date = models.DateField()
    current_medications = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    last_cancellation_time = models.DateTimeField(null=True, blank=True, help_text="Czas ostatniego anulowania wizyty")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.get_diabetes_type_display()}"

    def can_book_appointment(self):
        """Sprawdza czy pacjent może umówić wizytę (czy minęły 2 minuty od ostatniego anulowania)"""
        if not self.last_cancellation_time:
            return True

        time_since_cancellation = timezone.now() - self.last_cancellation_time
        return time_since_cancellation >= timedelta(minutes=2)

    def time_until_can_book(self):
        """Zwraca czas pozostały do możliwości umówienia wizyty"""
        if self.can_book_appointment():
            return None

        time_since_cancellation = timezone.now() - self.last_cancellation_time
        remaining_time = timedelta(minutes=2) - time_since_cancellation
        return remaining_time
    
    class Meta:
        verbose_name = "Pacjent"
        verbose_name_plural = "Pacjenci"
