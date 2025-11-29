#!/bin/bash
# ============================================
# AWX with Minikube Setup Script
# ============================================
# This script automates the AWX installation with Minikube
# Run with: bash setup-awx.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   AWX with Minikube Setup Script      ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  This script should NOT be run as root${NC}"
    echo -e "${YELLOW}⚠️  Some steps will request sudo when needed${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo -e "${YELLOW}Please install Docker first. See DOCKER_INSTALLATION_UBUNTU.md${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"
echo ""

# Check system resources
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM" -lt 4 ]; then
    echo -e "${YELLOW}⚠️  Warning: Your system has less than 4GB RAM${NC}"
    echo -e "${YELLOW}⚠️  AWX requires at least 4GB RAM (8GB recommended)${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Ask user if they want to continue
echo -e "${BLUE}This script will install:${NC}"
echo "  - Minikube (Kubernetes local cluster)"
echo "  - kubectl (Kubernetes CLI)"
echo "  - AWX Operator"
echo "  - AWX instance"
echo ""
echo -e "${YELLOW}Estimated time: 10-15 minutes${NC}"
echo -e "${YELLOW}Disk space needed: ~5GB${NC}"
echo ""

read -p "Continue with installation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Installation cancelled.${NC}"
    exit 0
fi

# Step 1: Install Minikube
echo ""
echo -e "${BLUE}📦 Step 1/7: Installing Minikube...${NC}"

if command -v minikube &> /dev/null; then
    echo -e "${GREEN}✅ Minikube already installed${NC}"
    minikube version
else
    echo -e "${BLUE}Downloading Minikube...${NC}"
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube
    rm minikube-linux-amd64
    echo -e "${GREEN}✅ Minikube installed${NC}"
fi

# Step 2: Install kubectl
echo ""
echo -e "${BLUE}📦 Step 2/7: Installing kubectl...${NC}"

if command -v kubectl &> /dev/null; then
    echo -e "${GREEN}✅ kubectl already installed${NC}"
    kubectl version --client --short 2>/dev/null || kubectl version --client
else
    echo -e "${BLUE}Downloading kubectl...${NC}"
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    rm kubectl
    echo -e "${GREEN}✅ kubectl installed${NC}"
fi

# Step 3: Start Minikube
echo ""
echo -e "${BLUE}🚀 Step 3/7: Starting Minikube...${NC}"

# Determine RAM allocation
if [ "$TOTAL_RAM" -ge 8 ]; then
    MEMORY=8192
else
    MEMORY=4096
fi

# Check if Minikube is already running
if minikube status &> /dev/null; then
    echo -e "${GREEN}✅ Minikube is already running${NC}"
else
    echo -e "${BLUE}Starting Minikube with ${MEMORY}MB RAM...${NC}"
    minikube start --cpus=4 --memory=${MEMORY} --disk-size=20g --driver=docker
    echo -e "${GREEN}✅ Minikube started${NC}"
fi

# Verify cluster
echo -e "${BLUE}Verifying cluster...${NC}"
kubectl get nodes

# Step 4: Create namespace and install AWX Operator
echo ""
echo -e "${BLUE}📦 Step 4/7: Installing AWX Operator...${NC}"

# Create namespace
if kubectl get namespace awx &> /dev/null; then
    echo -e "${GREEN}✅ Namespace 'awx' already exists${NC}"
else
    kubectl create namespace awx
    echo -e "${GREEN}✅ Namespace 'awx' created${NC}"
fi

# Install AWX Operator
echo -e "${BLUE}Installing AWX Operator (this may take a minute)...${NC}"
kubectl apply -f https://raw.githubusercontent.com/ansible/awx-operator/devel/deploy/awx-operator.yaml -n awx

# Wait for operator to be ready
echo -e "${BLUE}Waiting for AWX Operator to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/awx-operator-controller-manager -n awx || true

# Verify operator
kubectl get pods -n awx

echo -e "${GREEN}✅ AWX Operator installed${NC}"

# Step 5: Generate admin password
echo ""
echo -e "${BLUE}🔐 Step 5/7: Generating admin password...${NC}"

if kubectl get secret awx-admin-password -n awx &> /dev/null; then
    echo -e "${YELLOW}⚠️  Admin password secret already exists${NC}"
    ADMIN_PASSWORD="<existing>"
else
    ADMIN_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-24)
    kubectl create secret generic awx-admin-password \
        --from-literal=password="${ADMIN_PASSWORD}" \
        -n awx
    echo -e "${GREEN}✅ Admin password created${NC}"
fi

# Step 6: Deploy AWX
echo ""
echo -e "${BLUE}🎯 Step 6/7: Deploying AWX...${NC}"

# Check if AWX instance file exists
if [ ! -f "awx-instance.yaml" ]; then
    echo -e "${YELLOW}⚠️  awx-instance.yaml not found, creating default configuration...${NC}"
    cat > awx-instance.yaml <<EOF
---
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx
  namespace: awx
spec:
  service_type: NodePort
  nodeport_port: 30080
  web_resource_requirements:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1000m
      memory: 2Gi
  task_resource_requirements:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1000m
      memory: 2Gi
  postgres_storage_class: standard
  postgres_storage_requirements:
    requests:
      storage: 8Gi
  projects_persistence: true
  projects_storage_class: standard
  projects_storage_size: 8Gi
  admin_user: admin
  admin_password_secret: awx-admin-password
EOF
fi

# Apply AWX configuration
kubectl apply -f awx-instance.yaml -n awx

echo -e "${BLUE}Waiting for AWX to deploy (this may take 5-10 minutes)...${NC}"
echo -e "${YELLOW}You can monitor progress with: kubectl logs -f deployment/awx-operator-controller-manager -n awx${NC}"

# Wait for AWX pods to be created
sleep 30

# Wait for AWX to be ready (with timeout)
echo -e "${BLUE}Waiting for AWX pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=awx -n awx --timeout=600s || {
    echo -e "${YELLOW}⚠️  Timeout waiting for AWX, but deployment may still be in progress${NC}"
    echo -e "${YELLOW}⚠️  Check status with: kubectl get pods -n awx${NC}"
}

# Step 7: Display access information
echo ""
echo -e "${BLUE}📊 Step 7/7: Getting access information...${NC}"

# Wait a bit more
sleep 10

# Get service info
kubectl get svc -n awx
kubectl get pods -n awx

# Save credentials
if [ "$ADMIN_PASSWORD" != "<existing>" ]; then
    cat > awx-credentials.txt <<EOF
AWX Installation Credentials
=============================
Date: $(date)

Web Access:
  URL (NodePort): http://localhost:30080
  URL (Port Forward): Run 'kubectl port-forward svc/awx-service 8080:80 -n awx' then http://localhost:8080

  Username: admin
  Password: ${ADMIN_PASSWORD}

Minikube Access:
  Get URL: minikube service awx-service -n awx --url

Kubernetes Commands:
  View pods: kubectl get pods -n awx
  View logs: kubectl logs -f deployment/awx-web -n awx
  Port forward: kubectl port-forward svc/awx-service 8080:80 -n awx

IMPORTANT:
1. Keep this password safe!
2. Delete this file after saving credentials securely
3. Wait 2-3 minutes for AWX to fully initialize

Documentation: AWX_MINIKUBE_SETUP.md
EOF
    echo -e "${GREEN}✅ Credentials saved to awx-credentials.txt${NC}"
fi

# Final summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 AWX Installation Complete!        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Access AWX:${NC}"
echo ""
echo -e "${YELLOW}Method 1 - NodePort (default):${NC}"
echo "  http://localhost:30080"
echo ""
echo -e "${YELLOW}Method 2 - Port Forward:${NC}"
echo "  kubectl port-forward svc/awx-service 8080:80 -n awx"
echo "  http://localhost:8080"
echo ""
echo -e "${YELLOW}Method 3 - Minikube Service:${NC}"
echo "  minikube service awx-service -n awx --url"
echo ""
echo -e "${BLUE}Login Credentials:${NC}"
echo "  Username: ${GREEN}admin${NC}"
if [ "$ADMIN_PASSWORD" != "<existing>" ]; then
    echo "  Password: ${GREEN}${ADMIN_PASSWORD}${NC}"
else
    echo "  Password: ${YELLOW}<check existing secret>${NC}"
fi
echo ""
echo -e "${YELLOW}⚠️  Note: Wait 2-3 minutes for AWX to fully initialize before accessing${NC}"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  Check status:    kubectl get pods -n awx"
echo "  View logs:       kubectl logs -f deployment/awx-web -n awx"
echo "  Restart AWX:     kubectl rollout restart deployment/awx-web -n awx"
echo "  Stop Minikube:   minikube stop"
echo "  Start Minikube:  minikube start"
echo "  Delete AWX:      kubectl delete namespace awx"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Wait for AWX to fully initialize (2-3 minutes)"
echo "2. Access AWX web interface"
echo "3. Login with admin credentials"
echo "4. Configure your organization"
echo "5. Add your inventories and credentials"
echo "6. Import your Ansible playbooks"
echo "7. Create job templates"
echo "8. Integrate with NetBox (see AWX_MINIKUBE_SETUP.md)"
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}For Internet access with SSL, see: AWX_MINIKUBE_SETUP.md${NC}"
