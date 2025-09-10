from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('patient', 'Pacjent'),
        ('doctor', 'Lekarz'),
    )
    
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES,
        default='patient'
    )
    phone_number = models.CharField(max_length=15, blank=True)
    
    def is_patient(self):
        return self.user_type == 'patient'
    
    def is_doctor(self):
        return self.user_type == 'doctor'
