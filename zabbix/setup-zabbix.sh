#!/bin/bash
# ============================================
# Zabbix Quick Setup Script
# ============================================
# This script automates the Zabbix Docker setup
# Run with: bash setup-zabbix.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║  Zabbix 7.0 LTS Docker Setup Script   ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo -e "${YELLOW}Please install Docker first. See DOCKER_INSTALLATION_UBUNTU.md${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo -e "${YELLOW}Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"
echo -e "${GREEN}✅ Docker Compose is installed${NC}"
echo ""

# Set installation directory
INSTALL_DIR="${HOME}/zabbix-docker"

echo -e "${BLUE}📁 Installation directory: ${INSTALL_DIR}${NC}"
echo ""

# Ask user if they want to continue
read -p "Continue with installation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Installation cancelled.${NC}"
    exit 0
fi

# Create installation directory
echo -e "${BLUE}Creating installation directory...${NC}"
mkdir -p "${INSTALL_DIR}"
cd "${INSTALL_DIR}"

# Create subdirectories
mkdir -p postgres-data zabbix-scripts zabbix-modules

# Copy docker-compose.yml
echo -e "${BLUE}Copying docker-compose.yml...${NC}"
if [ -f "$(dirname "$0")/zabbix-docker-compose.yml" ]; then
    cp "$(dirname "$0")/zabbix-docker-compose.yml" "${INSTALL_DIR}/docker-compose.yml"
    echo -e "${GREEN}✅ docker-compose.yml copied${NC}"
else
    echo -e "${RED}❌ zabbix-docker-compose.yml not found!${NC}"
    exit 1
fi

# Copy and configure .env file
echo -e "${BLUE}Creating .env configuration file...${NC}"
if [ -f "$(dirname "$0")/zabbix-env.example" ]; then
    cp "$(dirname "$0")/zabbix-env.example" "${INSTALL_DIR}/.env"
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${RED}❌ zabbix-env.example not found!${NC}"
    exit 1
fi

# Generate secure password for PostgreSQL
echo -e "${BLUE}Generating secure database password...${NC}"
if command -v openssl &> /dev/null; then
    DB_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-24)
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${DB_PASSWORD}/" .env
    echo -e "${GREEN}✅ Database password generated${NC}"
else
    echo -e "${YELLOW}⚠️  OpenSSL not found. Using default password.${NC}"
    echo -e "${YELLOW}⚠️  Please change it in .env file!${NC}"
    DB_PASSWORD="zabbix"
fi

# Ask for server name
echo ""
echo -e "${BLUE}Server Configuration:${NC}"
read -p "Enter server name (default: Zabbix Monitoring Server): " SERVER_NAME
if [ -n "$SERVER_NAME" ]; then
    sed -i "s/ZBX_SERVER_NAME=.*/ZBX_SERVER_NAME=${SERVER_NAME}/" .env
fi

# Ask for timezone
read -p "Enter timezone (default: UTC, e.g., America/New_York): " TIMEZONE
if [ -n "$TIMEZONE" ]; then
    sed -i "s#PHP_TZ=.*#PHP_TZ=${TIMEZONE}#" .env
fi

echo ""
echo -e "${BLUE}Configuration Summary:${NC}"
echo "─────────────────────────────────────"
echo -e "Installation Directory: ${GREEN}${INSTALL_DIR}${NC}"
echo -e "Server Name: ${GREEN}${SERVER_NAME:-Zabbix Monitoring Server}${NC}"
echo -e "Timezone: ${GREEN}${TIMEZONE:-UTC}${NC}"
echo -e "Database Password: ${GREEN}${DB_PASSWORD}${NC}"
echo -e "Zabbix URL: ${GREEN}http://localhost:8080${NC}"
echo -e "Default Login: ${YELLOW}Admin / zabbix${NC}"
echo "─────────────────────────────────────"
echo ""

# Save credentials to file
cat > "${INSTALL_DIR}/CREDENTIALS.txt" <<EOF
Zabbix Installation Credentials
================================
Date: $(date)

Web Access:
  URL: http://localhost:8080
  Username: Admin
  Password: zabbix

Database:
  Username: zabbix
  Password: ${DB_PASSWORD}

IMPORTANT SECURITY NOTES:
1. Change the default Zabbix admin password immediately after first login!
2. Go to: User settings → Change password
3. Delete this file after saving the credentials securely!

First Steps:
1. Login to Zabbix web interface
2. Change admin password
3. Configure email notifications
4. Add your first hosts
5. Install Zabbix agents on monitored servers
6. Create dashboards

Documentation:
  Local: ${INSTALL_DIR}/../ZABBIX_DOCKER_SETUP.md
  Official: https://www.zabbix.com/documentation/7.0/
EOF

echo -e "${GREEN}✅ Credentials saved to ${INSTALL_DIR}/CREDENTIALS.txt${NC}"
echo ""

# Ask if user wants to start Zabbix now
read -p "Start Zabbix now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Starting Zabbix...${NC}"
    echo -e "${YELLOW}This may take 2-5 minutes on first run...${NC}"

    # Pull images
    echo -e "${BLUE}Pulling Docker images...${NC}"
    docker compose pull

    # Start services
    echo -e "${BLUE}Starting services...${NC}"
    docker compose up -d

    # Wait for services to be ready
    echo -e "${BLUE}Waiting for services to start...${NC}"
    sleep 15

    # Check status
    echo ""
    echo -e "${BLUE}Service Status:${NC}"
    docker compose ps

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🎉 Zabbix is starting!               ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Access Zabbix at:${NC} ${GREEN}http://localhost:8080${NC}"
    echo -e "${BLUE}Username:${NC} ${YELLOW}Admin${NC} ${RED}(with capital A!)${NC}"
    echo -e "${BLUE}Password:${NC} ${YELLOW}zabbix${NC}"
    echo ""
    echo -e "${RED}⚠️  CRITICAL: Change the admin password immediately after login!${NC}"
    echo ""
    echo -e "${YELLOW}Note: First startup may take 2-5 minutes${NC}"
    echo -e "${YELLOW}Wait for all services to be healthy before accessing the web interface${NC}"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo "  View logs:      docker compose logs -f"
    echo "  Stop Zabbix:    docker compose stop"
    echo "  Start Zabbix:   docker compose start"
    echo "  Status:         docker compose ps"
    echo "  Server logs:    docker compose logs -f zabbix-server"
    echo "  Web logs:       docker compose logs -f zabbix-web"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Wait 2-5 minutes for initialization"
    echo "2. Open http://localhost:8080 in your browser"
    echo "3. Login with Admin/zabbix"
    echo "4. CHANGE THE ADMIN PASSWORD (User settings → Change password)"
    echo "5. Configure email notifications (Administration → Media types → Email)"
    echo "6. Add your first host (Configuration → Hosts → Create host)"
    echo "7. Install Zabbix agent on hosts you want to monitor"
    echo "8. Create dashboards (Monitoring → Dashboards)"
else
    echo ""
    echo -e "${YELLOW}Zabbix not started.${NC}"
    echo -e "${BLUE}To start Zabbix later, run:${NC}"
    echo "  cd ${INSTALL_DIR}"
    echo "  docker compose up -d"
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}For Internet access with Nginx + SSL, see:${NC}"
echo "  ZABBIX_DOCKER_SETUP.md (section: Exposer Zabbix sur Internet)"
echo ""
echo -e "${BLUE}To monitor NetBox with Zabbix:${NC}"
echo "  1. Add NetBox server as a host in Zabbix"
echo "  2. Install Zabbix agent on NetBox server"
echo "  3. Apply 'Linux by Zabbix agent' template"
echo "  4. Monitor PostgreSQL database"
echo "  5. Monitor Docker containers"
