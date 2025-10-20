# 🏥 System Zarządzania Kliniką Diabetologiczną

System webowy do zarządzania wizytami i pacjentami w klinice diabetologicznej, zbudowany w Django 5.2.

## ✨ Funkcje

### 👤 Dla Pacjentów:
- ✅ Rejestracja z walidacją numeru PESEL
- ✅ Rezerwacja wizyt u wybranych lekarzy
- ✅ Edycja i anulowanie wizyt
- ✅ Historia wizyt
- ✅ Zarządzanie profilem
- ✅ Cooldown 2 minuty po anulowaniu wizyty

### 👨‍⚕️ Dla Lekarzy:
- ✅ Dashboard z statystykami
- ✅ Lista pacjentów
- ✅ Nadchodzące wizyty z grupowaniem po datach
- ✅ Szczegóły pacjentów z historią wizyt

### 🔐 Dla Administratorów:
- ✅ Panel zarządzania użytkownikami
- ✅ Blokowanie/odblokowywanie kont
- ✅ Zmiana ról użytkowników
- ✅ Reset haseł
- ✅ Statystyki systemu

## 🛡️ Bezpieczeństwo

- ✅ Blokada konta po 5 nieudanych próbach logowania (15 minut)
- ✅ Walidacja numeru PESEL z cyfrą kontrolną
- ✅ Sprawdzanie zgodności PESEL z datą urodzenia
- ✅ CSRF protection
- ✅ CORS headers
- ✅ Role-based access control

## 🚀 Quick Start

### 1. Klonowanie repozytorium:
```bash
git clone <repository-url>
cd diabetes_clinic_appointments
```

### 2. Utworzenie środowiska wirtualnego:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate  # Windows
```

### 3. Instalacja zależności:
```bash
pip install -r requirements.txt
```

### 4. Migracje bazy danych:
```bash
python manage.py migrate
```

### 5. Utworzenie superusera:
```bash
python manage.py createsuperuser
```

### 6. Uruchomienie serwera:
```bash
python manage.py runserver
```

### 7. Otwórz w przeglądarce:
```
http://127.0.0.1:8000/
```

## 🧪 Testowanie

### Uruchomienie wszystkich testów (121):
```bash
python manage.py test
```

### Uruchomienie testów dla konkretnego modułu:
```bash
# Testy modeli
python manage.py test authentication.tests doctors.tests patients.tests appointments.tests

# Testy widoków
python manage.py test authentication.test_views doctors.test_views patients.test_views appointments.test_views superadmin.test_views
```

### Uruchomienie z większą szczegółowością:
```bash
python manage.py test --verbosity=2
```

### Status testów:
✅ **121/121 testów przechodzi**
- 11 testów authentication
- 27 testów doctors
- 19 testów patients
- 39 testów appointments
- 25 testów superadmin

## 📁 Struktura Projektu

```
diabetes_clinic_appointments/
├── authentication/          # Logowanie, rejestracja, user model
├── patients/               # Moduł pacjentów
├── doctors/                # Moduł lekarzy
├── appointments/           # Zarządzanie wizytami
├── superadmin/             # Panel administratora
├── clinic_system/          # Główne ustawienia Django
├── static/                 # Pliki statyczne (CSS, JS)
├── templates/              # Szablony HTML
├── db.sqlite3             # Baza danych SQLite
└── manage.py              # Django management script
```

## 📊 Technologie

- **Backend**: Django 5.2
- **Database**: SQLite (dev) / PostgreSQL (production ready)
- **Frontend**: HTML, CSS, Bootstrap 5
- **Testing**: Django TestCase
- **Version Control**: Git

## 🔑 Role Użytkowników

### Patient (Pacjent)
- Może rejestrować się samodzielnie
- Zarządza własnymi wizytami
- Edytuje własny profil

### Doctor (Lekarz)
- Tworzony przez administratora
- Przegląda pacjentów i wizyty
- Dostęp do historii pacjentów

### Superadmin
- Pełna kontrola nad systemem
- Zarządzanie użytkownikami
- Dostęp do statystyk

## 📝 Walidacje

### PESEL:
- 11 cyfr
- Cyfra kontrolna zgodna z algorytmem
- Data urodzenia musi być zgodna z PESEL

### Wizyty:
- Tylko dni robocze (pon-pt)
- Godziny 8:00-17:00
- Maksymalnie 6 miesięcy w przód
- Sprawdzanie konfliktów czasowych

### Bezpieczeństwo:
- Automatyczna blokada po 5 nieudanych próbach
- Cooldown 2 minuty po anulowaniu wizyty
- Ochrona przed zmianą własnego konta (admin)

## 🐛 Debugging

### Django Shell:
```bash
python manage.py shell
```

### Sprawdzanie logów:
```bash
python manage.py runserver --verbosity=2
```

### Resetowanie bazy danych:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## 📈 Statystyki Projektu

- **Linie kodu**: ~5,000+
- **Testy**: 121 (wszystkie przechodzą ✅)
- **Pokrycie**: Modele 100%, Widoki 100%
- **Commits**: Clean git history

## 🔄 Git Workflow

### Ostatnie commity:
```bash
fef3418 - Testy integracyjne dla widoków (121 testów)
52230b5 - Testy integracyjne dla modeli
9a349a4 - Walidacja PESEL z cyfrą kontrolną
```

### Praca z git:
```bash
# Sprawdź status
git status

# Zobacz historię
git log --oneline -10

# Nowa funkcja
git checkout -b feature/nazwa
git add .
git commit -m "Opis zmian"
git push origin feature/nazwa
```

## 🚧 TODO / Roadmap

### Krótkoterminowe:
- [ ] Email notifications
- [ ] Export wizyt do PDF
- [ ] Kalendarz wizyt (FullCalendar.js)
- [ ] Dashboard z wykresami

### Długoterminowe:
- [ ] REST API (Django REST Framework)
- [ ] Aplikacja mobilna
- [ ] WebSockets dla powiadomień real-time
- [ ] Docker containerization
- [ ] CI/CD pipeline

## 📖 Dokumentacja

Szczegółowa dokumentacja dla programistów znajduje się w:
- `CONTEXT_PRACY_CLAUDE.md` - pełny kontekst projektu
- Inline comments w kodzie
- Docstrings w funkcjach i klasach

## 🤝 Contributing

1. Fork projektu
2. Stwórz branch (`git checkout -b feature/AmazingFeature`)
3. Commit zmian (`git commit -m 'Add some AmazingFeature'`)
4. Push do branch (`git push origin feature/AmazingFeature`)
5. Otwórz Pull Request

### Zasady:
- Pisz testy dla nowych funkcji (TDD)
- Wszystkie testy muszą przechodzić
- Używaj Black do formatowania kodu
- Dokumentuj zmiany

## 📞 Support

W razie problemów:
1. Sprawdź `CONTEXT_PRACY_CLAUDE.md`
2. Uruchom testy: `python manage.py test`
3. Sprawdź logi Django
4. Otwórz issue na GitHub

## 📄 License

Ten projekt jest rozwijany jako część portfolio edukacyjnego.

## 👨‍💻 Autor

**MarcinK420**
- GitHub: [@MarcinK420](https://github.com/MarcinK420)
- Data utworzenia: 2025-10-19
- Status: ✅ Produkcyjny (wszystkie testy przechodzą)

---

**Ostatnia aktualizacja**: 2025-10-19
**Wersja**: 1.0.0
**Status testów**: ✅ 121/121 przechodzi
