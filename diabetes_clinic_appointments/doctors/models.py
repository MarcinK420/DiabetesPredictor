from django.db import models
from django.conf import settings

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    license_number = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(
        max_length=50,
        choices=[
            ('endocrinologist', 'Endokrynolog'),
            ('diabetologist', 'Diabetolog'),
            ('internal_medicine', 'Internista'),
            ('family_medicine', 'Lekarz rodzinny'),
        ]
    )
    years_of_experience = models.PositiveIntegerField()
    office_address = models.TextField()
    consultation_fee = models.DecimalField(max_digits=6, decimal_places=2)
    
    working_hours_start = models.TimeField()
    working_hours_end = models.TimeField()
    working_days = models.CharField(
        max_length=20,
        choices=[
            ('mon-fri', 'Poniedziałek-Piątek'),
            ('mon-sat', 'Poniedziałek-Sobota'),
            ('tue-thu', 'Wtorek-Czwartek'),
        ],
        default='mon-fri'
    )
    
    education = models.TextField()
    certifications = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    is_accepting_patients = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} - {self.get_specialization_display()}"
    
    class Meta:
        verbose_name = "Lekarz"
        verbose_name_plural = "Lekarze"
