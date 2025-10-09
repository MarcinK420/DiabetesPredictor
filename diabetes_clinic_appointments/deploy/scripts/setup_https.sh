#!/bin/bash
# Setup HTTPS with Let's Encrypt for Clinic System
# This script automates the SSL certificate installation process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=""
EMAIL=""
WEBSERVER=""
PROJECT_PATH=""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Clinic System HTTPS Setup with Let's Encrypt${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

# Get domain
read -p "Enter your domain name (e.g., example.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}Error: Domain name is required${NC}"
    exit 1
fi

# Get email
read -p "Enter your email for Let's Encrypt notifications: " EMAIL
if [ -z "$EMAIL" ]; then
    echo -e "${RED}Error: Email is required${NC}"
    exit 1
fi

# Get webserver choice
echo ""
echo "Select your web server:"
echo "1) Nginx"
echo "2) Apache"
read -p "Enter choice (1 or 2): " WEBSERVER_CHOICE

if [ "$WEBSERVER_CHOICE" == "1" ]; then
    WEBSERVER="nginx"
elif [ "$WEBSERVER_CHOICE" == "2" ]; then
    WEBSERVER="apache2"
else
    echo -e "${RED}Error: Invalid choice${NC}"
    exit 1
fi

# Get project path
read -p "Enter full path to project (e.g., /var/www/clinic_system): " PROJECT_PATH
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}Error: Project path does not exist${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo "Web server: $WEBSERVER"
echo "Project path: $PROJECT_PATH"
echo ""
read -p "Continue with these settings? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Aborted."
    exit 0
fi

# Install Certbot
echo ""
echo -e "${GREEN}Step 1: Installing Certbot...${NC}"
if ! command -v certbot &> /dev/null; then
    apt-get update
    apt-get install -y certbot
    if [ "$WEBSERVER" == "nginx" ]; then
        apt-get install -y python3-certbot-nginx
    else
        apt-get install -y python3-certbot-apache
    fi
else
    echo "Certbot already installed"
fi

# Install Gunicorn if not present
echo ""
echo -e "${GREEN}Step 2: Checking Gunicorn...${NC}"
if [ ! -f "$PROJECT_PATH/venv/bin/gunicorn" ]; then
    echo "Installing Gunicorn..."
    $PROJECT_PATH/venv/bin/pip install gunicorn
else
    echo "Gunicorn already installed"
fi

# Create necessary directories
echo ""
echo -e "${GREEN}Step 3: Creating directories...${NC}"
mkdir -p /var/log/gunicorn
mkdir -p /var/www/certbot
chown -R www-data:www-data /var/log/gunicorn

# Setup systemd service
echo ""
echo -e "${GREEN}Step 4: Setting up systemd service...${NC}"
if [ -f "$PROJECT_PATH/deploy/systemd/gunicorn.socket" ]; then
    # Update paths in service files
    sed "s|/path/to/diabetes_clinic_appointments|$PROJECT_PATH|g" \
        "$PROJECT_PATH/deploy/systemd/gunicorn.service" > /etc/systemd/system/gunicorn-clinic-system.service

    cp "$PROJECT_PATH/deploy/systemd/gunicorn.socket" /etc/systemd/system/gunicorn-clinic-system.socket

    systemctl daemon-reload
    systemctl enable gunicorn-clinic-system.socket
    systemctl start gunicorn-clinic-system.socket
    echo "Systemd service configured"
else
    echo -e "${YELLOW}Warning: Systemd service files not found${NC}"
fi

# Configure web server
echo ""
echo -e "${GREEN}Step 5: Configuring $WEBSERVER...${NC}"
if [ "$WEBSERVER" == "nginx" ]; then
    # Setup Nginx
    NGINX_CONF="/etc/nginx/sites-available/clinic-system"
    sed "s|example.com|$DOMAIN|g; s|/path/to/diabetes_clinic_appointments|$PROJECT_PATH|g" \
        "$PROJECT_PATH/deploy/nginx/clinic_system.conf" > "$NGINX_CONF"

    # Create SSL params snippet
    mkdir -p /etc/nginx/snippets
    sed "s|example.com|$DOMAIN|g" \
        "$PROJECT_PATH/deploy/nginx/ssl-params.conf" > /etc/nginx/snippets/ssl-params.conf

    # Enable site
    ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/

    # Generate DH parameters (if not exists)
    if [ ! -f /etc/nginx/dhparam.pem ]; then
        echo -e "${YELLOW}Generating DH parameters (this may take a while)...${NC}"
        openssl dhparam -out /etc/nginx/dhparam.pem 2048
    fi

    nginx -t && systemctl reload nginx
else
    # Setup Apache
    APACHE_CONF="/etc/apache2/sites-available/clinic-system.conf"
    sed "s|example.com|$DOMAIN|g; s|/path/to/diabetes_clinic_appointments|$PROJECT_PATH|g" \
        "$PROJECT_PATH/deploy/apache/clinic_system.conf" > "$APACHE_CONF"

    # Enable required modules
    a2enmod ssl rewrite headers proxy proxy_http

    # Enable site
    a2ensite clinic-system.conf

    apache2ctl configtest && systemctl reload apache2
fi

# Obtain SSL certificate
echo ""
echo -e "${GREEN}Step 6: Obtaining SSL certificate...${NC}"
if [ "$WEBSERVER" == "nginx" ]; then
    certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive
else
    certbot --apache -d "$DOMAIN" -d "www.$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive
fi

# Setup automatic renewal
echo ""
echo -e "${GREEN}Step 7: Setting up automatic certificate renewal...${NC}"
if ! crontab -l | grep -q "certbot renew"; then
    (crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload $WEBSERVER'") | crontab -
    echo "Automatic renewal configured"
else
    echo "Automatic renewal already configured"
fi

# Update Django settings
echo ""
echo -e "${GREEN}Step 8: Updating Django settings...${NC}"
if grep -q "TRUST_PROXY_HEADERS=False" "$PROJECT_PATH/.env"; then
    sed -i 's/TRUST_PROXY_HEADERS=False/TRUST_PROXY_HEADERS=True/' "$PROJECT_PATH/.env"
    echo "Updated TRUST_PROXY_HEADERS to True"
fi

if grep -q "DJANGO_ENVIRONMENT=development" "$PROJECT_PATH/.env"; then
    echo -e "${YELLOW}Warning: .env still set to development. Consider changing to production.${NC}"
fi

# Collect static files
echo ""
echo -e "${GREEN}Step 9: Collecting static files...${NC}"
cd "$PROJECT_PATH"
source venv/bin/activate
python manage.py collectstatic --noinput
deactivate

# Final checks
echo ""
echo -e "${GREEN}Step 10: Running final checks...${NC}"
systemctl status gunicorn-clinic-system.socket --no-pager
systemctl status $WEBSERVER --no-pager

# Success message
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}HTTPS Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Your site should now be accessible at:"
echo -e "${GREEN}https://$DOMAIN${NC}"
echo ""
echo "Certificate will auto-renew every 60 days."
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update .env file: set DJANGO_ENVIRONMENT=production"
echo "2. Update .env file: set ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN"
echo "3. Restart Gunicorn: sudo systemctl restart gunicorn-clinic-system"
echo "4. Test your site: curl -I https://$DOMAIN"
echo "5. Check SSL rating: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo ""
