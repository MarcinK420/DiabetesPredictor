# HTTPS Setup Guide - Clinic System

Ten przewodnik opisuje jak skonfigurować HTTPS dla aplikacji Clinic System w środowisku produkcyjnym.

## Spis treści

1. [Wymagania wstępne](#wymagania-wstępne)
2. [Metoda 1: Automatyczna konfiguracja (Zalecana)](#metoda-1-automatyczna-konfiguracja)
3. [Metoda 2: Manualna konfiguracja z Nginx](#metoda-2-manualna-konfiguracja-z-nginx)
4. [Metoda 3: Manualna konfiguracja z Apache](#metoda-3-manualna-konfiguracja-z-apache)
5. [Cloudflare SSL](#cloudflare-ssl)
6. [Self-signed certificates (Development/Staging)](#self-signed-certificates)
7. [Troubleshooting](#troubleshooting)
8. [Testowanie konfiguracji](#testowanie-konfiguracji)

---

## Wymagania wstępne

### Zanim zaczniesz:

- ✅ Serwer z Ubuntu/Debian (lub inną dystrybucją Linux)
- ✅ Domena wskazująca na serwer (rekordy A/AAAA w DNS)
- ✅ Otwarte porty 80 i 443 w firewall
- ✅ Zainstalowany Python 3.8+
- ✅ Aplikacja sklonowana i skonfigurowana
- ✅ Root lub sudo access

### Sprawdź DNS:

```bash
# Sprawdź czy domena wskazuje na Twój serwer
dig +short yourdomain.com
```

---

## Metoda 1: Automatyczna konfiguracja (Zalecana)

Używamy gotowego skryptu, który automatycznie skonfiguruje HTTPS z Let's Encrypt.

### Krok 1: Uruchom skrypt

```bash
cd /path/to/diabetes_clinic_appointments
sudo bash deploy/scripts/setup_https.sh
```

Skrypt zapyta o:
- **Domenę** (np. example.com)
- **Email** (dla powiadomień Let's Encrypt)
- **Web server** (Nginx lub Apache)
- **Ścieżkę projektu** (np. /var/www/clinic_system)

### Krok 2: Zaktualizuj .env

Po zakończeniu skryptu, edytuj `.env`:

```bash
nano .env
```

Ustaw:
```env
DJANGO_ENVIRONMENT=production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
TRUST_PROXY_HEADERS=True
```

### Krok 3: Restart Gunicorn

```bash
sudo systemctl restart gunicorn-clinic-system
```

### Krok 4: Testuj

```bash
curl -I https://yourdomain.com
```

✅ **Gotowe!** Twoja aplikacja działa na HTTPS.

---

## Metoda 2: Manualna konfiguracja z Nginx

### Krok 1: Zainstaluj wymagane pakiety

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

### Krok 2: Zainstaluj Gunicorn

```bash
source venv/bin/activate
pip install gunicorn
deactivate
```

### Krok 3: Skonfiguruj Gunicorn Systemd

Skopiuj i dostosuj pliki systemd:

```bash
# Zamień /path/to/diabetes_clinic_appointments na rzeczywistą ścieżkę
sudo sed 's|/path/to/diabetes_clinic_appointments|'$(pwd)'|g' \
    deploy/systemd/gunicorn.service > /etc/systemd/system/gunicorn-clinic-system.service

sudo cp deploy/systemd/gunicorn.socket /etc/systemd/system/gunicorn-clinic-system.socket

# Uruchom
sudo systemctl daemon-reload
sudo systemctl enable gunicorn-clinic-system.socket
sudo systemctl start gunicorn-clinic-system.socket
sudo systemctl status gunicorn-clinic-system.socket
```

### Krok 4: Skonfiguruj Nginx (tymczasowo bez SSL)

```bash
# Utwórz tymczasową konfigurację dla certbot
sudo tee /etc/nginx/sites-available/clinic-system <<EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'Server is running';
        add_header Content-Type text/plain;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/clinic-system /etc/nginx/sites-enabled/
sudo mkdir -p /var/www/certbot
sudo nginx -t
sudo systemctl reload nginx
```

### Krok 5: Uzyskaj certyfikat SSL

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Krok 6: Zastosuj pełną konfigurację Nginx

```bash
# Zamień example.com na swoją domenę
sudo sed 's|example.com|yourdomain.com|g; s|/path/to/diabetes_clinic_appointments|'$(pwd)'|g' \
    deploy/nginx/clinic_system.conf > /etc/nginx/sites-available/clinic-system

# Utwórz SSL params
sudo mkdir -p /etc/nginx/snippets
sudo sed 's|example.com|yourdomain.com|g' \
    deploy/nginx/ssl-params.conf > /etc/nginx/snippets/ssl-params.conf

# Wygeneruj DH parameters
sudo openssl dhparam -out /etc/nginx/dhparam.pem 2048

# Testuj i restart
sudo nginx -t
sudo systemctl reload nginx
```

### Krok 7: Zaktualizuj .env i restart Django

```bash
# Edytuj .env
nano .env
```

Ustaw:
```env
DJANGO_ENVIRONMENT=production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
TRUST_PROXY_HEADERS=True
SECURE_SSL_REDIRECT=True
```

```bash
# Zbierz static files
source venv/bin/activate
python manage.py collectstatic --noinput
deactivate

# Restart Gunicorn
sudo systemctl restart gunicorn-clinic-system
```

### Krok 8: Automatyczne odnawianie certyfikatu

```bash
# Dodaj cron job dla auto-renewal
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
```

---

## Metoda 3: Manualna konfiguracja z Apache

### Krok 1: Zainstaluj wymagane pakiety

```bash
sudo apt update
sudo apt install -y apache2 certbot python3-certbot-apache
```

### Krok 2: Zainstaluj Gunicorn

(Ten sam jak w Metodzie 2, Krok 2)

### Krok 3: Skonfiguruj Gunicorn Systemd

(Ten sam jak w Metodzie 2, Krok 3)

### Krok 4: Skonfiguruj Apache (tymczasowo bez SSL)

```bash
sudo tee /etc/apache2/sites-available/clinic-system.conf <<EOF
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com

    Alias /.well-known/acme-challenge/ /var/www/certbot/.well-known/acme-challenge/
    <Directory /var/www/certbot/.well-known/acme-challenge/>
        Require all granted
    </Directory>
</VirtualHost>
EOF

sudo mkdir -p /var/www/certbot
sudo a2ensite clinic-system.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

### Krok 5: Uzyskaj certyfikat SSL

```bash
sudo certbot --apache -d yourdomain.com -d www.yourdomain.com
```

### Krok 6: Zastosuj pełną konfigurację Apache

```bash
# Zamień example.com na swoją domenę
sudo sed 's|example.com|yourdomain.com|g; s|/path/to/diabetes_clinic_appointments|'$(pwd)'|g' \
    deploy/apache/clinic_system.conf > /etc/apache2/sites-available/clinic-system.conf

# Włącz wymagane moduły
sudo a2enmod ssl rewrite headers proxy proxy_http

# Testuj i restart
sudo apache2ctl configtest
sudo systemctl reload apache2
```

### Krok 7-8: Jak w Metodzie 2

---

## Cloudflare SSL

Jeśli używasz Cloudflare jako proxy/CDN:

### Opcja 1: Cloudflare Full (Strict) - Zalecane

1. **W Cloudflare Dashboard:**
   - SSL/TLS → Overview → Full (strict)
   - SSL/TLS → Edge Certificates → Always Use HTTPS: ON
   - SSL/TLS → Edge Certificates → Minimum TLS Version: 1.2

2. **Na serwerze:**
   - Zainstaluj Origin Certificate z Cloudflare
   - Lub użyj Let's Encrypt (metoda 2 lub 3)

3. **W .env:**
```env
TRUST_PROXY_HEADERS=True
SECURE_SSL_REDIRECT=False  # Cloudflare już przekierowuje
```

### Opcja 2: Cloudflare Flexible - Nie zalecane

```env
TRUST_PROXY_HEADERS=True
SECURE_SSL_REDIRECT=False
# UWAGA: Ruch między Cloudflare a serwerem NIE jest szyfrowany
```

---

## Self-signed Certificates

Dla development/staging (NIE dla produkcji!):

### Generowanie certyfikatu

```bash
sudo mkdir -p /etc/ssl/private
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/selfsigned.key \
    -out /etc/ssl/certs/selfsigned.crt \
    -subj "/C=PL/ST=Mazowieckie/L=Warsaw/O=Clinic/CN=localhost"
```

### Nginx config dla self-signed

```nginx
server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate /etc/ssl/certs/selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/selfsigned.key;

    # ... reszta konfiguracji
}
```

### W .env

```env
DJANGO_ENVIRONMENT=development
TRUST_PROXY_HEADERS=False
SECURE_SSL_REDIRECT=False
```

---

## Troubleshooting

### Problem: "Connection refused" na porcie 443

**Rozwiązanie:**
```bash
# Sprawdź firewall
sudo ufw status
sudo ufw allow 443/tcp

# Sprawdź czy nginx/apache słucha
sudo netstat -tlnp | grep :443
```

### Problem: "502 Bad Gateway"

**Rozwiązanie:**
```bash
# Sprawdź status Gunicorn
sudo systemctl status gunicorn-clinic-system

# Sprawdź logi
sudo journalctl -u gunicorn-clinic-system -f

# Restart
sudo systemctl restart gunicorn-clinic-system
```

### Problem: "SSL certificate problem"

**Rozwiązanie:**
```bash
# Sprawdź certyfikat
sudo certbot certificates

# Odnów ręcznie
sudo certbot renew --force-renewal
```

### Problem: Django zwraca "CSRF verification failed"

**Rozwiązanie:**

W `.env` upewnij się że:
```env
TRUST_PROXY_HEADERS=True
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Problem: Static files nie ładują się

**Rozwiązanie:**
```bash
# Zbierz static files
source venv/bin/activate
python manage.py collectstatic --noinput
deactivate

# Sprawdź uprawnienia
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/
```

---

## Testowanie konfiguracji

### 1. Test podstawowy

```bash
# HTTP powinien przekierować na HTTPS
curl -I http://yourdomain.com

# HTTPS powinien zwrócić 200
curl -I https://yourdomain.com
```

### 2. Test SSL/TLS

```bash
# Sprawdź certyfikat
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Sprawdź protokoły
nmap --script ssl-enum-ciphers -p 443 yourdomain.com
```

### 3. Test HSTS

```bash
curl -I https://yourdomain.com | grep -i "strict-transport"
# Powinno zwrócić: strict-transport-security: max-age=31536000; includeSubDomains; preload
```

### 4. Test online

- **SSL Labs:** https://www.ssllabs.com/ssltest/
- **Security Headers:** https://securityheaders.com/
- **HTTP Security Report:** https://httpsecurityreport.com/

**Cel:** Ocena A lub A+ na SSL Labs

### 5. Test Django

```bash
# Sprawdź deployment checklist
DJANGO_ENVIRONMENT=production python manage.py check --deploy
```

---

## Monitoring i utrzymanie

### Sprawdzanie statusu certyfikatu

```bash
sudo certbot certificates
```

### Logi

```bash
# Nginx
sudo tail -f /var/log/nginx/clinic_system_error.log

# Apache
sudo tail -f /var/log/apache2/clinic_system_error.log

# Gunicorn
sudo journalctl -u gunicorn-clinic-system -f

# Django
tail -f logs/django.log
```

### Backup certyfikatów

```bash
sudo tar -czf letsencrypt-backup.tar.gz /etc/letsencrypt
```

---

## Najlepsze praktyki

1. ✅ **Zawsze używaj Let's Encrypt** w produkcji (darmowe, automatyczne odnawianie)
2. ✅ **Włącz HSTS** (już skonfigurowane w production.py)
3. ✅ **Używaj TLS 1.2+** (starsze wersje są niebezpieczne)
4. ✅ **Monitoruj ważność certyfikatu** (Let's Encrypt: 90 dni)
5. ✅ **Testuj konfigurację** na SSL Labs regularnie
6. ✅ **Backup certyfikatów** przed większymi zmianami
7. ✅ **Używaj Cloudflare** dla dodatkowej ochrony DDoS (opcjonalnie)

---

## Dodatkowe zasoby

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [OWASP TLS Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html)
- [Django Security Settings](https://docs.djangoproject.com/en/stable/topics/security/)

---

**Masz pytania lub problemy?** Sprawdź sekcję [Troubleshooting](#troubleshooting) lub stwórz issue w repozytorium projektu.
