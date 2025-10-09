# Konfiguracja środowisk Development / Production

Projekt obsługuje dwa środowiska: **development** i **production**.

## Struktura plików konfiguracyjnych

```
clinic_system/
└── settings/
    ├── __init__.py        # Automatyczny wybór środowiska
    ├── base.py            # Wspólne ustawienia
    ├── development.py     # Ustawienia dla development
    └── production.py      # Ustawienia dla production
```

## Przełączanie między środowiskami

Środowisko jest określane przez zmienną `DJANGO_ENVIRONMENT` w pliku `.env`:

- `DJANGO_ENVIRONMENT=development` (domyślne)
- `DJANGO_ENVIRONMENT=production`

## Development (Środowisko deweloperskie)

### Konfiguracja .env dla development:

```env
DJANGO_ENVIRONMENT=development
SECRET_KEY='your-secret-key-here'
```

### Cechy środowiska development:
- ✅ DEBUG=True
- ✅ ALLOWED_HOSTS=['*'] (wszystkie hosty dozwolone)
- ✅ SQLite database
- ✅ Verbose logging do konsoli
- ✅ Email backend: konsola (wiadomości wyświetlane w konsoli)

### Uruchomienie development:

```bash
source venv/bin/activate
python manage.py runserver
```

## Production (Środowisko produkcyjne)

### Konfiguracja .env dla production:

```env
DJANGO_ENVIRONMENT=production
SECRET_KEY='długi-losowy-bezpieczny-klucz-produkcyjny'
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Opcjonalne: PostgreSQL database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

# Email settings (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=your-email@example.com
```

### Cechy środowiska production:
- ✅ DEBUG=False
- ✅ ALLOWED_HOSTS musi być ustawione (wymagane!)
- ✅ SQLite lub PostgreSQL (przez DATABASE_URL)
- ✅ Zaawansowane zabezpieczenia (HTTPS, HSTS, secure cookies)
- ✅ Logging do pliku (katalog `logs/`)
- ✅ Email backend: SMTP

### Wymagania dla production:

1. **Wygeneruj nowy SECRET_KEY:**
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

2. **Ustaw ALLOWED_HOSTS:**
   - Lista domen oddzielonych przecinkami
   - Przykład: `ALLOWED_HOSTS=example.com,www.example.com,192.168.1.1`

3. **Skonfiguruj HTTPS:**
   - Zobacz szczegółowy przewodnik: [HTTPS_SETUP.md](HTTPS_SETUP.md)
   - Automatyczna konfiguracja: `sudo bash deploy/scripts/setup_https.sh`
   - Lub manualna konfiguracja z Nginx/Apache

4. **Opcjonalnie: Użyj PostgreSQL:**
   ```bash
   pip install psycopg2-binary
   ```
   Ustaw DATABASE_URL w .env:
   ```
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```

5. **Zbierz pliki statyczne:**
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Uruchom migracje:**
   ```bash
   python manage.py migrate
   ```

### Deploy check:

```bash
# Sprawdź konfigurację produkcyjną
DJANGO_ENVIRONMENT=production python manage.py check --deploy
```

## Zależności

Instalacja wymaganych paczek:

```bash
pip install -r requirements.txt
```

Podstawowe zależności:
- `django>=5.2.6`
- `python-dotenv>=1.1.1`
- `dj-database-url>=3.0.1` (dla PostgreSQL)
- `psycopg2-binary` (dla PostgreSQL, opcjonalne)

## Logi

### Development:
- Logi są wyświetlane w konsoli
- Poziom: INFO

### Production:
- Logi są zapisywane do `logs/django.log`
- Maksymalny rozmiar: 15MB (rotacja 10 plików)
- Poziom: WARNING
- Logi bezpieczeństwa: osobny handler

## Bezpieczeństwo w Production

Środowisko production automatycznie aktywuje następujące zabezpieczenia:

- **SECURE_SSL_REDIRECT**: Przekierowanie HTTP → HTTPS
- **SESSION_COOKIE_SECURE**: Secure cookies dla sesji
- **CSRF_COOKIE_SECURE**: Secure cookies dla CSRF
- **SECURE_HSTS_SECONDS**: HTTP Strict Transport Security (1 rok)
- **SECURE_BROWSER_XSS_FILTER**: Ochrona XSS
- **X_FRAME_OPTIONS**: Ochrona przed clickjacking
- **SECURE_REFERRER_POLICY**: Kontrola informacji referrer
- **SECURE_CROSS_ORIGIN_OPENER_POLICY**: Ochrona cross-origin
- **SECURE_PROXY_SSL_HEADER**: Wsparcie dla reverse proxy (opcjonalne)

### Konfiguracja HTTPS

Szczegółowy przewodnik konfiguracji HTTPS znajduje się w [HTTPS_SETUP.md](HTTPS_SETUP.md).

**Szybki start:**
```bash
sudo bash deploy/scripts/setup_https.sh
```

Skrypt automatycznie:
- Instaluje Let's Encrypt certbot
- Konfiguruje Nginx lub Apache
- Uzyskuje darmowy certyfikat SSL
- Ustawia automatyczne odnawianie
- Konfiguruje Gunicorn systemd service

## Troubleshooting

### Błąd: "ALLOWED_HOSTS environment variable must be set in production!"
➡️ Ustaw zmienną ALLOWED_HOSTS w pliku .env

### Błąd: "Unable to configure handler 'file'"
➡️ Upewnij się, że katalog `logs/` istnieje (tworzony automatycznie przez settings)

### Błąd: "dj-database-url is required when using DATABASE_URL"
➡️ Zainstaluj: `pip install dj-database-url`

## Zmienne środowiskowe - pełna lista

| Zmienna | Development | Production | Opis |
|---------|------------|------------|------|
| DJANGO_ENVIRONMENT | development | production | Określa środowisko |
| SECRET_KEY | ✅ Wymagane | ✅ Wymagane | Klucz bezpieczeństwa Django |
| ALLOWED_HOSTS | - | ✅ Wymagane | Lista dozwolonych hostów |
| DATABASE_URL | - | Opcjonalne | URL do bazy PostgreSQL |
| SECURE_SSL_REDIRECT | - | Opcjonalne (True) | Przekierowanie na HTTPS |
| SECURE_HSTS_SECONDS | - | Opcjonalne (31536000) | HSTS timeout |
| TRUST_PROXY_HEADERS | - | Opcjonalne (False) | Zaufaj X-Forwarded-* headers |
| SECURE_REFERRER_POLICY | - | Opcjonalne (same-origin) | Polityka referrer |
| SECURE_CROSS_ORIGIN_OPENER_POLICY | - | Opcjonalne (same-origin) | COOP policy |
| CSRF_TRUSTED_ORIGINS | - | Opcjonalne | Lista zaufanych origins dla CSRF |
| CSRF_COOKIE_HTTPONLY | - | Opcjonalne (False) | HttpOnly flag dla CSRF cookie |
| CSRF_COOKIE_SAMESITE | - | Opcjonalne (Lax) | SameSite policy dla CSRF |
| CSRF_COOKIE_AGE | - | Opcjonalne (31449600) | Czas życia CSRF cookie |
| CORS_ALLOWED_ORIGINS | - | Opcjonalne | Lista dozwolonych CORS origins |
| CORS_ALLOW_CREDENTIALS | - | Opcjonalne (True) | Allow credentials w CORS |
| CORS_ALLOWED_METHODS | - | Opcjonalne | Dozwolone HTTP metody dla CORS |
| CORS_ALLOWED_HEADERS | - | Opcjonalne | Dozwolone headers dla CORS |
| CORS_EXPOSE_HEADERS | - | Opcjonalne | Exposed headers dla CORS |
| ENABLE_CORS_IN_DEV | False | - | Włącz CORS w development |
| CORS_ALLOW_ALL_ORIGINS_DEV | True | - | Allow all origins w dev |
| EMAIL_HOST | - | Opcjonalne | Serwer SMTP |
| EMAIL_PORT | - | Opcjonalne (587) | Port SMTP |
| EMAIL_USE_TLS | - | Opcjonalne (True) | Użycie TLS |
| EMAIL_HOST_USER | - | Opcjonalne | Login SMTP |
| EMAIL_HOST_PASSWORD | - | Opcjonalne | Hasło SMTP |
| DEFAULT_FROM_EMAIL | - | Opcjonalne | Domyślny nadawca |

## Deployment Configurations

Projekt zawiera gotowe konfiguracje dla popularnych deployment scenarios:

```
deploy/
├── nginx/
│   ├── clinic_system.conf    # Nginx + SSL config
│   └── ssl-params.conf        # SSL parameters
├── apache/
│   └── clinic_system.conf     # Apache + SSL config
├── systemd/
│   ├── gunicorn.service       # Gunicorn systemd service
│   └── gunicorn.socket        # Gunicorn socket
└── scripts/
    └── setup_https.sh         # Automatyczna konfiguracja HTTPS
```

Zobacz [HTTPS_SETUP.md](HTTPS_SETUP.md) dla szczegółowych instrukcji.

## CSRF i CORS

### CSRF (Cross-Site Request Forgery) Protection

Django ma wbudowaną ochronę CSRF. Projekt konfiguruje dodatkowe zabezpieczenia:

**Production:**
- `CSRF_COOKIE_SECURE=True` - Cookie tylko przez HTTPS
- `CSRF_TRUSTED_ORIGINS` - Lista zaufanych domen (auto-generowana z ALLOWED_HOSTS)
- `CSRF_COOKIE_SAMESITE=Lax` - Ochrona przed CSRF attacks

**Development:**
- `CSRF_COOKIE_SECURE=False` - Zezwól na HTTP
- Predefiniowana lista trusted origins (localhost:8000, localhost:3000)

**Konfiguracja CSRF_TRUSTED_ORIGINS:**
```env
# Dla produkcji - lista domen z https://
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com,https://api.example.com
```

### CORS (Cross-Origin Resource Sharing)

CORS jest wymagane **tylko** jeśli masz:
- Oddzielny frontend (React, Vue, Angular)
- Aplikację mobilną
- Zewnętrzne API konsumenty

**Kiedy NIE potrzebujesz CORS:**
- Monolityczna aplikacja Django (templates + views)
- Frontend renderowany przez Django

#### Scenariusz 1: Aplikacja monolityczna (domyślnie)

CORS jest **wyłączone**. Nie musisz nic konfigurować.

#### Scenariusz 2: Django API + React/Vue frontend

**Production (.env):**
```env
# Włącz CORS dla konkretnych domen
CORS_ALLOWED_ORIGINS=https://frontend.example.com,https://app.example.com
CORS_ALLOW_CREDENTIALS=True
```

**Development (.env):**
```env
# Włącz CORS w development
ENABLE_CORS_IN_DEV=True
CORS_ALLOW_ALL_ORIGINS_DEV=True  # Lub False dla konkretnych origins
```

#### Scenariusz 3: Public API (bez credentials)

```env
CORS_ALLOWED_ORIGINS=*  # Lub konkretne domeny
CORS_ALLOW_CREDENTIALS=False  # Brak cookies/auth
CORS_ALLOWED_METHODS=GET,POST,OPTIONS
```

#### Scenariusz 4: Mobile App

```env
# Mobile apps często używają localhost w development
CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,capacitor://localhost
CORS_ALLOW_CREDENTIALS=True
```

### Testowanie CSRF i CORS

**Test CSRF:**
```bash
# Powinno zwrócić błąd CSRF
curl -X POST https://yourdomain.com/api/endpoint/

# Poprawne użycie (z CSRF token)
curl -X POST https://yourdomain.com/api/endpoint/ \
  -H "X-CSRFToken: your-token" \
  -H "Cookie: csrftoken=your-token"
```

**Test CORS:**
```bash
# Sprawdź CORS headers
curl -I -X OPTIONS https://yourdomain.com/api/endpoint/ \
  -H "Origin: https://frontend.example.com"

# Powinno zwrócić:
# Access-Control-Allow-Origin: https://frontend.example.com
# Access-Control-Allow-Credentials: true
```

### Troubleshooting CSRF/CORS

**Problem: "CSRF verification failed"**
- Sprawdź czy `CSRF_TRUSTED_ORIGINS` zawiera Twoją domenę z https://
- Sprawdź czy frontend wysyła CSRF token w header `X-CSRFToken`

**Problem: "CORS policy: No 'Access-Control-Allow-Origin'"**
- Sprawdź czy `CORS_ALLOWED_ORIGINS` zawiera origin frontendu
- Sprawdź czy `corsheaders` jest w INSTALLED_APPS
- Sprawdź czy `CorsMiddleware` jest w MIDDLEWARE (przed CommonMiddleware)

**Problem: "CORS credentials mode mismatch"**
- Ustaw `CORS_ALLOW_CREDENTIALS=True` jeśli używasz cookies/auth
- Frontend musi wysyłać `credentials: 'include'` w fetch/axios
