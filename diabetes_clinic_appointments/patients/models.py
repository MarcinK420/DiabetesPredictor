from django.db import models
from django.conf import settings

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.get_diabetes_type_display()}"
    
    class Meta:
        verbose_name = "Pacjent"
        verbose_name_plural = "Pacjenci"
