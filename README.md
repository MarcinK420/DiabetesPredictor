# 🏥 Diabetes Clinic Appointments - System Rezerwacji Wizyt

## 📋 Opis Projektu

System kliniki diabetologicznej umożliwiający pacjentom zarządzanie wizytami, przeglądanie profilu medycznego oraz komunikację z lekarzami. Projekt został zaimplementowany w Django z pełną funkcjonalnością CRUD, systemem autoryzacji i zaawansowanymi mechanizmami bezpieczeństwa.

## ✨ Zaimplementowane Wymagania Funkcjonalne

### ✅ **FR-06: Zapisywanie się na wizytę** (Priorytet: M)
- **Opis**: Formularz rezerwacji wizyty z wyborem lekarza, daty i powodu wizyty
- **URL**: `/appointments/book/`
- **Funkcjonalności**:
  - Wybór dostępnych lekarzy (tylko aktywni)
  - Walidacja terminów (8:00-17:00, pon-pt)
  - Sprawdzanie konfliktów terminów
  - Komunikat "Pomyślnie zapisano"
- **Pliki**: `appointments/views.py:book_appointment`, `appointments/forms.py:AppointmentBookingForm`

### ✅ **FR-07: Edycja wizyty** (Priorytet: M)
- **Opis**: Możliwość edycji zaplanowanych wizyt z pełną walidacją
- **URL**: `/appointments/edit/<id>/`
- **Funkcjonalności**:
  - Edycja tylko przyszłych wizyt o statusie 'scheduled'
  - Walidacja dostępności nowego terminu
  - Wyklucza aktualnie edytowaną wizytę z konfliktu
  - Komunikat "Zapisano zmiany"
- **Pliki**: `appointments/views.py:edit_appointment`, `appointments/forms.py:AppointmentEditForm`

### ✅ **FR-08: Anulowanie wizyty** (Priorytet: M)
- **Opis**: System anulowania z potwierdzeniem i mechanizmem cooldown
- **URL**: `/appointments/cancel/<id>/`
- **Funkcjonalności**:
  - Potwierdzenie "Czy na pewno chcesz anulować?" (TAK/NIE)
  - 2-minutowy cooldown przed następnym zapisem
  - Komunikat "Pomyślnie odwołano"
  - Aktualizacja statusu wizyty na 'cancelled'
- **Pliki**: `appointments/views.py:cancel_appointment`, `patients/models.py:last_cancellation_time`

### ✅ **FR-09: Karta z danymi pacjenta** (Priorytet: N)
- **Opis**: Profil pacjenta z danymi osobowymi, medycznymi i bezpieczeństwem
- **URL**: `/patients/profile/`
- **Funkcjonalności**:
  - Dane osobowe (imię, nazwisko, wiek, adres)
  - Informacje medyczne (typ cukrzycy, leki, alergie)
  - Kontakt awaryjny
  - Maskowanie wrażliwych danych (PESEL)
  - Statystyki wizyt
  - Edycja profilu (`/patients/profile/edit/`)
- **Pliki**: `patients/views.py:profile`, `patients/forms.py:PatientProfileForm`

### ✅ **FR-10: Strona główna pacjenta** (Priorytet: W)
- **Opis**: Dashboard z nawigacją i powitaniem "Dzień dobry"
- **URL**: `/patients/dashboard/`
- **Funkcjonalności**:
  - Powitanie "Dzień dobry, [Imię]!"
  - Karty nawigacyjne: Profil, Wizyty, Historia Wizyt
  - Statystyki (nadchodzące wizyty, łączna liczba, wiek)
  - Informacje o najbliższej wizycie
  - Responsive design z hover effects
- **Pliki**: `patients/views.py:dashboard`, `patients/templates/patients/dashboard.html`

## 🏗️ Architektura Aplikacji

### Aplikacje Django
```
clinic_system/           # Main project directory
├── authentication/     # System logowania i autoryzacji
├── patients/           # Zarządzanie danymi pacjentów
├── doctors/           # Zarządzanie danymi lekarzy
└── appointments/      # System rezerwacji wizyt
```

### Modele Danych

#### **User (authentication.models)**
```python
- user_type: CharField (patient/doctor)
- phone_number: CharField
- is_patient() / is_doctor() methods
```

#### **Patient (patients.models)**
```python
- user: OneToOneField(User)
- date_of_birth: DateField
- pesel: CharField (unique)
- address: TextField
- emergency_contact: CharField + phone
- diabetes_type: CharField (type1/type2/gestational)
- diagnosis_date: DateField
- current_medications: TextField
- allergies: TextField
- last_cancellation_time: DateTimeField  # FR-08
```

#### **Doctor (doctors.models)**
```python
- user: OneToOneField(User)
- license_number: CharField (unique)
- specialization: CharField
- years_of_experience: PositiveIntegerField
- office_address: TextField
- consultation_fee: DecimalField
- working_hours: TimeFields
- working_days: CharField
```

#### **Appointment (appointments.models)**
```python
- patient: ForeignKey(Patient)
- doctor: ForeignKey(Doctor)
- appointment_date: DateTimeField
- status: CharField (scheduled/completed/cancelled/no_show)
- reason: CharField
- notes: TextField
- duration_minutes: PositiveIntegerField
```

## 🔐 System Bezpieczeństwa

### Autoryzacja
- **Pacjenci**: Dostęp tylko do własnych danych i wizyt
- **Lekarze**: Dostęp do danych swoich pacjentów
- **Superuser**: Pełny dostęp administracyjny

### Ochrona Danych (FR-09)
- **Maskowanie PESEL**: `85****45` zamiast pełnego numeru
- **Kontrola dostępu**: `Patient.can_be_viewed_by(user)`
- **Wrażliwe pola**: Lista pól wymagających dodatkowej ochrony
- **Walidacja formularzy**: Sprawdzanie poprawności danych

### Mechanizmy Cooldown (FR-08)
- **2-minutowy cooldown** po anulowaniu wizyty
- **Blokada UI** podczas okresu ograniczenia
- **Wizualny countdown** w dashboard i formularzach

## 📊 Funkcjonalności Systemu

### Zarządzanie Wizytami
1. **Rezerwacja** (FR-06) - pełna walidacja terminów
2. **Edycja** (FR-07) - modyfikacja szczegółów wizyty
3. **Anulowanie** (FR-08) - z potwierdzeniem i cooldown
4. **Historia** - przeglądanie poprzednich wizyt
5. **Nadchodzące** - lista zaplanowanych terminów

### Profil Pacjenta (FR-09)
1. **Wyświetlanie** - kompletne dane osobowe i medyczne
2. **Edycja** - modyfikacja wybranych pól
3. **Bezpieczeństwo** - maskowanie wrażliwych danych
4. **Statystyki** - informacje o wizytach

### Dashboard (FR-10)
1. **Powitanie** - personalizowane "Dzień dobry"
2. **Nawigacja** - karty do głównych sekcji
3. **Statystyki** - przegląd kluczowych danych
4. **Szybkie akcje** - najczęściej używane funkcje

## 🛣️ Routing URLs

```python
# Main URLs
/patients/dashboard/              # FR-10: Dashboard pacjenta
/patients/profile/               # FR-09: Profil pacjenta
/patients/profile/edit/          # FR-09: Edycja profilu

/appointments/book/              # FR-06: Rezerwacja wizyty
/appointments/edit/<id>/         # FR-07: Edycja wizyty
/appointments/cancel/<id>/       # FR-08: Anulowanie wizyty
/appointments/upcoming/          # Lista nadchodzących wizyt
/appointments/history/           # Historia wizyt
/appointments/detail/<id>/       # Szczegóły wizyty

/auth/login/                     # Logowanie
/auth/logout/                    # Wylogowanie
```

## 📝 Formularze

### **AppointmentBookingForm** (FR-06)
- Wybór lekarza z dostępnych
- Data i godzina wizyty
- Powód wizyty
- Walidacja konfliktów i godzin pracy

### **AppointmentEditForm** (FR-07)
- Podobny do booking, ale z ID wizyty
- Wyklucza aktualną wizytę z walidacji konfliktów

### **PatientProfileForm** (FR-09)
- Dane User: imię, nazwisko, email, telefon
- Dane Patient: adres, kontakt awaryjny, leki, alergie
- Atomiczne zapisywanie obu modeli

## 🎨 Frontend Features

### Design System
- **Bootstrap 5** - responsive grid i komponenty
- **FontAwesome** - ikony i symbole
- **Custom CSS** - hover effects i transitions
- **Color coding** - różne kolory dla statusów i typów

### User Experience
- **Hover effects** - karty unoszą się po najechaniu
- **Loading states** - disabled buttons podczas cooldown
- **Success/Error messages** - komunikaty zwrotne
- **Breadcrumb navigation** - łatwa nawigacja
- **Mobile responsive** - działa na wszystkich urządzeniach

## ⚙️ Konfiguracja Środowiska

### Wymagania
```
Django==5.2.6
Python 3.13+
SQLite (development)
```

### Ustawienia
- **Language**: Polski (pl)
- **Timezone**: Europe/Warsaw
- **Auth Model**: Custom User (authentication.User)
- **Login URLs**: Konfigurowane przekierowania

## 🚀 Instalacja i Uruchomienie

```bash
# Aktywacja środowiska wirtualnego
source venv/bin/activate

# Migracje bazy danych
python manage.py migrate

# Uruchomienie serwera
python manage.py runserver

# Sprawdzenie systemu
python manage.py check
```

## 📈 Status Implementacji

### Zakończone (✅)
- FR-06: Zapisywanie się na wizytę
- FR-07: Edycja wizyty
- FR-08: Anulowanie wizyty
- FR-09: Karta z danymi pacjenta
- FR-10: Strona główna pacjenta

### Do implementacji
- FR-11: Strona główna lekarza
- FR-12: Najbliższe wizyty (dla lekarza)
- FR-13: Spis pacjentów
- FR-14: Podejrzenie karty pacjenta
- FR-15: Wprowadzanie wyników

## 🔧 Kluczowe Pliki

### Views
- `patients/views.py` - Dashboard, profil, edycja profilu
- `appointments/views.py` - CRUD wizyt (book, edit, cancel)

### Models
- `patients/models.py` - Patient model z metodami pomocniczymi
- `appointments/models.py` - Appointment model
- `authentication/models.py` - Custom User model

### Templates
- `patients/templates/patients/dashboard.html` - FR-10
- `patients/templates/patients/profile.html` - FR-09
- `appointments/templates/appointments/book_appointment.html` - FR-06
- `appointments/templates/appointments/edit_appointment.html` - FR-07
- `appointments/templates/appointments/cancel_appointment.html` - FR-08

### Forms
- `appointments/forms.py` - AppointmentBookingForm, AppointmentEditForm
- `patients/forms.py` - PatientProfileForm

## 📋 Notatki Techniczne

### Walidacja Biznesowa
- **Godziny pracy**: 8:00-17:00, poniedziałek-piątek
- **Czas wizyty**: 30 minut + 15 minut buffer
- **Cooldown**: 2 minuty po anulowaniu
- **Dostępność**: Max 6 miesięcy w przyszłość

### Bezpieczeństwo Danych
- PESEL maskowany jako `XX****XX`
- Tylko właściciel może edytować swój profil
- Lekarze widzą tylko swoich pacjentów
- Walidacja uprawnień na poziomie view

### Performance
- Optymalizowane zapytania z select_related
- Paginacja dla długich list
- Indeksowanie kluczowych pól

---

**Autor**: Marcin Kruk
**Wersja**: v1.0 (Implementacja FR-06 do FR-10)
**Data**: 13.09.2025

*System przygotowany zgodnie z wymaganiami funkcjonalnymi i gotowy do rozszerzenia o kolejne funkcje.*