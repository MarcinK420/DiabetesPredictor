from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

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

    # Pola do śledzenia nieudanych prób logowania
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)

    def is_patient(self):
        return self.user_type == 'patient'

    def is_doctor(self):
        return self.user_type == 'doctor'

    def is_account_locked(self):
        """Sprawdza czy konto jest zablokowane"""
        if self.account_locked_until:
            if timezone.now() < self.account_locked_until:
                return True
            else:
                # Odblokuj konto po upływie czasu
                self.failed_login_attempts = 0
                self.account_locked_until = None
                self.save()
                return False
        return False

    def increment_failed_login(self):
        """Zwiększa licznik nieudanych prób logowania"""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()

        if self.failed_login_attempts >= 5:
            # Blokada na 15 minut po 5 nieudanych próbach
            self.account_locked_until = timezone.now() + timedelta(minutes=15)

        self.save()

    def reset_failed_login(self):
        """Resetuje licznik nieudanych prób logowania"""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.account_locked_until = None
        self.save()
