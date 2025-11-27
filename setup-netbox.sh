#!/bin/bash
# ============================================
# NetBox Quick Setup Script
# ============================================
# This script automates the NetBox Docker setup
# Run with: bash setup-netbox.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   NetBox Docker Setup Script          ║"
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
INSTALL_DIR="${HOME}/netbox-docker"

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
mkdir -p postgres-data redis-data netbox-media netbox-reports netbox-scripts

# Copy docker-compose.yml
echo -e "${BLUE}Copying docker-compose.yml...${NC}"
if [ -f "$(dirname "$0")/docker-compose.yml" ]; then
    cp "$(dirname "$0")/docker-compose.yml" "${INSTALL_DIR}/"
    echo -e "${GREEN}✅ docker-compose.yml copied${NC}"
else
    echo -e "${RED}❌ docker-compose.yml not found!${NC}"
    exit 1
fi

# Copy and configure .env file
echo -e "${BLUE}Creating .env configuration file...${NC}"
if [ -f "$(dirname "$0")/env.example" ]; then
    cp "$(dirname "$0")/env.example" "${INSTALL_DIR}/.env"
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${RED}❌ env.example not found!${NC}"
    exit 1
fi

# Generate a secure secret key
echo -e "${BLUE}Generating secure SECRET_KEY...${NC}"
if command -v python3 &> /dev/null; then
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
elif command -v openssl &> /dev/null; then
    SECRET_KEY=$(openssl rand -base64 48)
else
    echo -e "${RED}❌ Cannot generate SECRET_KEY. Please install python3 or openssl.${NC}"
    exit 1
fi

# Update SECRET_KEY in .env
sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
echo -e "${GREEN}✅ SECRET_KEY generated and saved${NC}"

# Generate secure passwords
echo -e "${BLUE}Generating secure passwords...${NC}"
if command -v openssl &> /dev/null; then
    DB_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-24)
    SUPERUSER_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)

    sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/" .env
    sed -i "s/SUPERUSER_PASSWORD=.*/SUPERUSER_PASSWORD=${SUPERUSER_PASSWORD}/" .env
    echo -e "${GREEN}✅ Passwords generated${NC}"
else
    echo -e "${YELLOW}⚠️  OpenSSL not found. Using default passwords.${NC}"
    echo -e "${YELLOW}⚠️  Please change them in .env file!${NC}"
fi

echo ""
echo -e "${BLUE}Configuration Summary:${NC}"
echo "─────────────────────────────────────"
echo -e "Installation Directory: ${GREEN}${INSTALL_DIR}${NC}"
echo -e "Admin Username: ${GREEN}admin${NC}"
echo -e "Admin Password: ${GREEN}${SUPERUSER_PASSWORD:-admin}${NC}"
echo -e "Database Password: ${GREEN}${DB_PASSWORD:-netbox123}${NC}"
echo -e "NetBox URL: ${GREEN}http://localhost:8000${NC}"
echo "─────────────────────────────────────"
echo ""

# Save credentials to file
cat > "${INSTALL_DIR}/CREDENTIALS.txt" <<EOF
NetBox Installation Credentials
================================
Date: $(date)

Admin Login:
  Username: admin
  Password: ${SUPERUSER_PASSWORD:-admin}

Database:
  Username: netbox
  Password: ${DB_PASSWORD:-netbox123}

Access URL:
  http://localhost:8000

IMPORTANT: Keep this file secure and delete it after saving the credentials!
EOF

echo -e "${GREEN}✅ Credentials saved to ${INSTALL_DIR}/CREDENTIALS.txt${NC}"
echo ""

# Ask if user wants to start NetBox now
read -p "Start NetBox now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Starting NetBox...${NC}"
    echo -e "${YELLOW}This may take a few minutes on first run...${NC}"

    # Pull images
    echo -e "${BLUE}Pulling Docker images...${NC}"
    docker compose pull

    # Start services
    echo -e "${BLUE}Starting services...${NC}"
    docker compose up -d

    # Wait for services to be ready
    echo -e "${BLUE}Waiting for services to start...${NC}"
    sleep 10

    # Check status
    echo ""
    echo -e "${BLUE}Service Status:${NC}"
    docker compose ps

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🎉 NetBox is starting!               ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Access NetBox at:${NC} ${GREEN}http://localhost:8000${NC}"
    echo -e "${BLUE}Username:${NC} ${GREEN}admin${NC}"
    echo -e "${BLUE}Password:${NC} ${GREEN}${SUPERUSER_PASSWORD:-admin}${NC}"
    echo ""
    echo -e "${YELLOW}Note: First startup may take 2-5 minutes${NC}"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo "  View logs:    docker compose logs -f"
    echo "  Stop NetBox:  docker compose stop"
    echo "  Start NetBox: docker compose start"
    echo "  Status:       docker compose ps"
else
    echo ""
    echo -e "${YELLOW}NetBox not started.${NC}"
    echo -e "${BLUE}To start NetBox later, run:${NC}"
    echo "  cd ${INSTALL_DIR}"
    echo "  docker compose up -d"
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
