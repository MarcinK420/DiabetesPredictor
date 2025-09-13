#!/usr/bin/env python
"""
Script to create sample data for testing FR-04 Historia wizyt
Creates user mkruk with password 12345 and sample appointments
"""
import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from authentication.models import User
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment

def create_sample_data():
    print("Creating sample data...")
    
    # Create mkruk user
    print("1. Creating user mkruk...")
    user, created = User.objects.get_or_create(
        username='mkruk',
        defaults={
            'first_name': 'Marcin',
            'last_name': 'Kruk',
            'email': 'mkruk@example.com',
            'user_type': 'patient',
            'phone_number': '+48123456789'
        }
    )
    if created:
        user.set_password('12345')
        user.save()
        print(f"✓ Created user: {user.username}")
    else:
        print(f"✓ User already exists: {user.username}")
    
    # Create patient profile for mkruk
    print("2. Creating patient profile...")
    patient, created = Patient.objects.get_or_create(
        user=user,
        defaults={
            'date_of_birth': '1990-05-15',
            'pesel': '90051512345',
            'address': 'ul. Warszawska 123\n00-001 Warszawa',
            'emergency_contact_name': 'Anna Kruk',
            'emergency_contact_phone': '+48987654321',
            'diabetes_type': 'type2',
            'diagnosis_date': '2020-03-10',
            'current_medications': 'Metformina 500mg 2x dziennie\nInsulin Glargine 20j wieczorem',
            'allergies': 'Penicilin - wysypka'
        }
    )
    if created:
        print(f"✓ Created patient profile for: {patient.user.get_full_name()}")
    else:
        print(f"✓ Patient profile already exists for: {patient.user.get_full_name()}")
    
    # Get or create a doctor
    print("3. Getting doctor...")
    try:
        doctor = Doctor.objects.first()
        if not doctor:
            # Create sample doctor
            doctor_user = User.objects.create_user(
                username='doctor1',
                first_name='Anna',
                last_name='Kowalska',
                email='a.kowalska@clinic.com',
                user_type='doctor',
                password='doctor123'
            )
            doctor = Doctor.objects.create(
                user=doctor_user,
                license_number='PWZ123456',
                specialization='diabetologist',
                years_of_experience=10,
                office_address='ul. Medyczna 5\n00-002 Warszawa\nGabinet 201',
                consultation_fee=200.00,
                working_hours_start='08:00',
                working_hours_end='16:00',
                working_days='mon-fri',
                education='Uniwersytet Medyczny w Warszawie\nSpecjalizacja: Diabetologia',
                certifications='Certyfikat Europejskiego Towarzystwa Diabetologicznego',
                bio='Doświadczony diabetolog z 10-letnim stażem. Specjalizuje się w leczeniu cukrzycy typu 1 i 2.'
            )
            print(f"✓ Created doctor: Dr. {doctor.user.get_full_name()}")
        else:
            print(f"✓ Using existing doctor: Dr. {doctor.user.get_full_name()}")
    except Exception as e:
        print(f"✗ Error creating doctor: {e}")
        return
    
    # Create sample appointments
    print("4. Creating sample appointments...")
    now = timezone.now()
    
    appointments_data = [
        {
            'appointment_date': now - timedelta(days=30),
            'status': 'completed',
            'reason': 'Kontrola poziomu cukru we krwi',
            'notes': 'Pacjent zgłasza stabilne wartości glukozy. HbA1c: 7.2%. Zalecam kontynuację obecnej terapii. Następna kontrola za 3 miesiące.',
            'duration_minutes': 45
        },
        {
            'appointment_date': now - timedelta(days=60),
            'status': 'completed',
            'reason': 'Konsultacja diabetologiczna - wyniki badań',
            'notes': 'Omówiono wyniki badań laboratoryjnych. Dostosowano dawkę insuliny wieczornej do 22j. Pacjent edukowany w zakresie diety.',
            'duration_minutes': 60
        },
        {
            'appointment_date': now - timedelta(days=90),
            'status': 'completed',
            'reason': 'Pierwsza wizyta - diagnoza cukrzycy',
            'notes': 'Rozpoznano cukrzycę typu 2. Rozpoczęto leczenie Metforminą. Pacjent otrzymał glukometr i został przeszkolony z jego obsługi.',
            'duration_minutes': 90
        },
        {
            'appointment_date': now + timedelta(days=30),
            'status': 'scheduled',
            'reason': 'Kontrola trimestralna - badania kontrolne',
            'notes': '',
            'duration_minutes': 30
        },
        {
            'appointment_date': now + timedelta(days=7),
            'status': 'scheduled',
            'reason': 'Konsultacja w sprawie diety',
            'notes': '',
            'duration_minutes': 45
        }
    ]
    
    created_count = 0
    for appointment_data in appointments_data:
        appointment, created = Appointment.objects.get_or_create(
            patient=patient,
            doctor=doctor,
            appointment_date=appointment_data['appointment_date'],
            defaults=appointment_data
        )
        if created:
            created_count += 1
            print(f"✓ Created appointment: {appointment_data['reason']} - {appointment_data['appointment_date'].strftime('%Y-%m-%d %H:%M')}")
    
    print(f"\n✓ Created {created_count} new appointments")
    print(f"✓ Total appointments for {user.username}: {Appointment.objects.filter(patient=patient).count()}")
    print(f"\nSample data creation completed!")
    print(f"You can now login with username: mkruk, password: 12345")

if __name__ == "__main__":
    create_sample_data()