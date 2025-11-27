#!/bin/bash
# ============================================
# NetBox Nginx + SSL Setup Script
# ============================================
# This script automates Nginx and SSL configuration for NetBox

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║  NetBox Nginx + SSL Setup Script      ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run this script as root or with sudo${NC}"
    exit 1
fi

# Check if NetBox is running
if ! docker compose -f ~/netbox-docker/docker-compose.yml ps | grep -q "netbox.*Up"; then
    echo -e "${YELLOW}⚠️  NetBox doesn't seem to be running${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Ask for domain name
echo ""
echo -e "${BLUE}📝 Configuration${NC}"
echo "─────────────────────────────────────"
read -p "Enter your domain name (e.g., netbox.example.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ Domain name is required${NC}"
    exit 1
fi

# Ask for email (for Let's Encrypt)
read -p "Enter your email address (for SSL certificate): " EMAIL

if [ -z "$EMAIL" ]; then
    echo -e "${RED}❌ Email is required for Let's Encrypt${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  Domain: ${GREEN}${DOMAIN}${NC}"
echo "  Email: ${GREEN}${EMAIL}${NC}"
echo ""

read -p "Continue with installation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Installation cancelled${NC}"
    exit 0
fi

# Update system
echo ""
echo -e "${BLUE}📦 Updating system packages...${NC}"
apt update

# Install Nginx
echo -e "${BLUE}📦 Installing Nginx...${NC}"
apt install -y nginx

# Enable and start Nginx
systemctl enable nginx
systemctl start nginx

# Configure firewall
echo -e "${BLUE}🔥 Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 'Nginx Full'
    ufw allow OpenSSH
    echo "y" | ufw enable || true
    ufw status
fi

# Create Nginx configuration
echo -e "${BLUE}⚙️  Creating Nginx configuration...${NC}"

cat > /etc/nginx/sites-available/netbox <<EOF
# NetBox Nginx Configuration
upstream netbox {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;

    server_name ${DOMAIN};

    access_log /var/log/nginx/netbox_access.log;
    error_log /var/log/nginx/netbox_error.log;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
        allow all;
    }

    location / {
        proxy_pass http://netbox;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;

        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;

        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    client_max_body_size 25m;
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/netbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo -e "${BLUE}🧪 Testing Nginx configuration...${NC}"
nginx -t

# Reload Nginx
systemctl reload nginx

echo -e "${GREEN}✅ Nginx configured successfully${NC}"

# Install Certbot
echo ""
echo -e "${BLUE}📦 Installing Certbot for SSL...${NC}"
apt install -y certbot python3-certbot-nginx

# Get SSL certificate
echo ""
echo -e "${BLUE}🔒 Obtaining SSL certificate from Let's Encrypt...${NC}"
certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --email ${EMAIL} --redirect

# Test auto-renewal
echo -e "${BLUE}🔄 Testing SSL auto-renewal...${NC}"
certbot renew --dry-run

# Update NetBox .env file
echo ""
echo -e "${BLUE}⚙️  Updating NetBox configuration...${NC}"

NETBOX_DIR="${HOME}/netbox-docker"
if [ ! -d "$NETBOX_DIR" ]; then
    NETBOX_DIR="/root/netbox-docker"
fi

if [ -f "${NETBOX_DIR}/.env" ]; then
    # Backup .env
    cp ${NETBOX_DIR}/.env ${NETBOX_DIR}/.env.backup

    # Update ALLOWED_HOSTS
    if grep -q "ALLOWED_HOSTS=" ${NETBOX_DIR}/.env; then
        sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=${DOMAIN},localhost/" ${NETBOX_DIR}/.env
    else
        echo "ALLOWED_HOSTS=${DOMAIN},localhost" >> ${NETBOX_DIR}/.env
    fi

    # Update CORS
    if grep -q "CORS_ORIGIN_ALLOW_ALL=" ${NETBOX_DIR}/.env; then
        sed -i "s/CORS_ORIGIN_ALLOW_ALL=.*/CORS_ORIGIN_ALLOW_ALL=False/" ${NETBOX_DIR}/.env
    fi

    echo -e "${GREEN}✅ NetBox .env updated${NC}"

    # Restart NetBox
    echo -e "${BLUE}🔄 Restarting NetBox...${NC}"
    cd ${NETBOX_DIR}
    docker compose down
    docker compose up -d

    echo -e "${GREEN}✅ NetBox restarted${NC}"
else
    echo -e "${YELLOW}⚠️  Could not find NetBox .env file. Please update manually.${NC}"
fi

# Install Fail2Ban
echo ""
read -p "Install Fail2Ban for additional security? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}📦 Installing Fail2Ban...${NC}"
    apt install -y fail2ban

    # Create Fail2Ban config
    cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF

    systemctl enable fail2ban
    systemctl start fail2ban
    echo -e "${GREEN}✅ Fail2Ban installed and configured${NC}"
fi

# Final summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 Installation Complete!            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}NetBox Access:${NC}"
echo "  URL: ${GREEN}https://${DOMAIN}${NC}"
echo "  Username: ${GREEN}admin${NC}"
echo "  Password: ${YELLOW}(as configured in .env)${NC}"
echo ""
echo -e "${BLUE}SSL Certificate:${NC}"
echo "  Status: ${GREEN}Active${NC}"
echo "  Auto-renewal: ${GREEN}Enabled${NC}"
echo "  Expires in: ${GREEN}90 days${NC}"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  Check Nginx status:  ${YELLOW}sudo systemctl status nginx${NC}"
echo "  Check SSL cert:      ${YELLOW}sudo certbot certificates${NC}"
echo "  View Nginx logs:     ${YELLOW}sudo tail -f /var/log/nginx/netbox_access.log${NC}"
echo "  View NetBox logs:    ${YELLOW}cd ~/netbox-docker && docker compose logs -f${NC}"
echo ""
echo -e "${GREEN}✅ Your NetBox instance is now securely accessible from the Internet!${NC}"
