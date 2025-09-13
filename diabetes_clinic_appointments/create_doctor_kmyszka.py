#!/usr/bin/env python
"""
Script to create doctor profile for Kacper Myszka (kmyszka / 12345)
"""
import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from authentication.models import User
from doctors.models import Doctor

def create_doctor_kmyszka():
    print("Creating doctor profile for Kacper Myszka...")
    
    # Create kmyszka user
    print("1. Creating user kmyszka...")
    user, created = User.objects.get_or_create(
        username='kmyszka',
        defaults={
            'first_name': 'Kacper',
            'last_name': 'Myszka',
            'email': 'k.myszka@clinic.com',
            'user_type': 'doctor',
            'phone_number': '+48555123456'
        }
    )
    
    if created:
        user.set_password('12345')
        user.save()
        print(f"✓ Created user: {user.username}")
    else:
        print(f"✓ User already exists: {user.username}")
    
    # Create doctor profile for kmyszka
    print("2. Creating doctor profile...")
    doctor, created = Doctor.objects.get_or_create(
        user=user,
        defaults={
            'license_number': 'PWZ987654',
            'specialization': 'endocrinologist',
            'years_of_experience': 8,
            'office_address': 'ul. Diabetologiczna 12\n00-005 Warszawa\nPokój 305',
            'consultation_fee': 250.00,
            'working_hours_start': '09:00',
            'working_hours_end': '17:00',
            'working_days': 'mon-fri',
            'education': 'Uniwersytet Medyczny w Krakowie\nSpecjalizacja: Endokrynologia\nDoktorat: Leczenie cukrzycy typu 2',
            'certifications': 'Certyfikat Polskiego Towarzystwa Diabetologicznego\nCertyfikat Europejskiej Akademii Endokrynologii\nKurs prowadzenia pomp insulinowych',
            'bio': 'Doświadczony endokrynolog specjalizujący się w kompleksowym leczeniu cukrzycy wszystkich typów. Szczególnie zainteresowany nowoczesnymi technologiami w diabetologii, w tym systemami ciągłego monitorowania glukozy i pompami insulinowymi. Prowadzi badania nad optymalizacją leczenia insulinowego.',
            'is_accepting_patients': True
        }
    )
    
    if created:
        print(f"✓ Created doctor profile for: Dr. {doctor.user.get_full_name()}")
    else:
        print(f"✓ Doctor profile already exists for: Dr. {doctor.user.get_full_name()}")
    
    print(f"\n✓ Doctor creation completed!")
    print(f"Login: kmyszka")
    print(f"Password: 12345")
    print(f"Type: Doctor ({doctor.get_specialization_display()})")
    print(f"Experience: {doctor.years_of_experience} years")

if __name__ == "__main__":
    create_doctor_kmyszka()