from django.db import models
from django.conf import settings
from patients.models import Patient
from doctors.models import Doctor

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Zaplanowana'),
        ('completed', 'Zakończona'),
        ('cancelled', 'Anulowana'),
        ('no_show', 'Niestawiennictwo'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    reason = models.CharField(max_length=200, help_text="Powód wizyty")
    notes = models.TextField(blank=True, help_text="Notatki z wizyty")
    duration_minutes = models.PositiveIntegerField(default=30)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date']
        verbose_name = "Wizyta"
        verbose_name_plural = "Wizyty"
    
    def __str__(self):
        return f"{self.patient.user.first_name} {self.patient.user.last_name} - {self.appointment_date.strftime('%Y-%m-%d %H:%M')} - Dr. {self.doctor.user.last_name}"
