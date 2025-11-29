# AWX, NetBox & Zabbix Docker Installation Guide

Guides d'installation complètes pour Docker, NetBox v4.4.7, Zabbix 7.0 LTS et AWX avec Docker Compose.
Complete installation guides for Docker, NetBox v4.4.7, Zabbix 7.0 LTS, and AWX with Docker Compose.

## 📚 Documentation / Documentation

### 🐳 Docker Installation / Installation Docker
- **[DOCKER_INSTALLATION_UBUNTU.md](DOCKER_INSTALLATION_UBUNTU.md)** - Guide complet d'installation de Docker sur Ubuntu / Complete Docker installation guide for Ubuntu

### 📦 NetBox v4.4.7 Installation / Installation NetBox v4.4.7
- **[NETBOX_DOCKER_SETUP.md](NETBOX_DOCKER_SETUP.md)** - Guide d'installation et configuration de NetBox v4.4.7 / NetBox v4.4.7 installation and configuration guide
- **[NETBOX_V4_FEATURES.md](NETBOX_V4_FEATURES.md)** - Nouveautés et fonctionnalités de NetBox v4.x / NetBox v4.x features and what's new
- **[NETBOX_INTERNET_ACCESS.md](NETBOX_INTERNET_ACCESS.md)** - 🌐 Exposer NetBox sur Internet avec Nginx et SSL / Expose NetBox to Internet with Nginx and SSL
- **[docker-compose.yml](docker-compose.yml)** - Fichier Docker Compose complet pour NetBox / Complete Docker Compose file for NetBox
- **[env.example](env.example)** - Exemple de configuration d'environnement / Environment configuration example
- **[nginx-configs/](nginx-configs/)** - Configurations Nginx prêtes à l'emploi / Ready-to-use Nginx configurations

### 📊 Zabbix 7.0 LTS Installation / Installation Zabbix 7.0 LTS
- **[ZABBIX_DOCKER_SETUP.md](ZABBIX_DOCKER_SETUP.md)** - Guide d'installation et configuration de Zabbix 7.0 LTS / Zabbix 7.0 LTS installation and configuration guide
- **[zabbix-docker-compose.yml](zabbix-docker-compose.yml)** - Fichier Docker Compose complet pour Zabbix / Complete Docker Compose file for Zabbix
- **[zabbix-env.example](zabbix-env.example)** - Exemple de configuration d'environnement pour Zabbix / Zabbix environment configuration example

### 🤖 AWX (Ansible Tower) Installation / Installation AWX
- **[AWX_MINIKUBE_SETUP.md](AWX_MINIKUBE_SETUP.md)** - Guide d'installation et configuration d'AWX avec Minikube / AWX with Minikube installation and configuration guide
- **[awx-instance.yaml](awx-instance.yaml)** - Configuration AWX Kubernetes / AWX Kubernetes configuration
- **[awx-ingress.yaml](awx-ingress.yaml)** - Configuration Ingress pour AWX (optionnel) / Ingress configuration for AWX (optional)

## 🚀 Quick Start / Démarrage Rapide

### 1. Install Docker / Installer Docker
```bash
# Follow the guide / Suivez le guide
cat DOCKER_INSTALLATION_UBUNTU.md
```

### 2. Setup NetBox / Configurer NetBox
```bash
# Create directory / Créer le répertoire
mkdir -p ~/netbox-docker
cd ~/netbox-docker

# Copy files / Copier les fichiers
cp docker-compose.yml ~/netbox-docker/
cp env.example ~/netbox-docker/.env

# Edit configuration / Modifier la configuration
nano .env

# Generate secret key / Générer une clé secrète
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Start NetBox / Démarrer NetBox
docker compose up -d

# Access / Accéder
# http://localhost:8000
```

### 3. Default Credentials / Identifiants par défaut
- Username / Utilisateur: `admin`
- Password / Mot de passe: (as configured in .env / tel que configuré dans .env)

## 🌐 Internet Access / Accès Internet

### Pour VPS Cloud / For Cloud VPS

Si vous voulez accéder à NetBox depuis Internet (VPS cloud):
If you want to access NetBox from the Internet (cloud VPS):

```bash
# Installation automatique avec Nginx + SSL
sudo bash setup-nginx-ssl.sh

# Ou suivez le guide détaillé
# Or follow the detailed guide
cat NETBOX_INTERNET_ACCESS.md
```

**Ce que vous obtenez / What you get:**
- ✅ Nginx reverse proxy configuré / Nginx reverse proxy configured
- ✅ Certificat SSL gratuit (Let's Encrypt) / Free SSL certificate (Let's Encrypt)
- ✅ HTTPS sécurisé avec redirection HTTP / Secure HTTPS with HTTP redirect
- ✅ Pare-feu configuré / Firewall configured
- ✅ Headers de sécurité / Security headers
- ✅ Renouvellement automatique SSL / Automatic SSL renewal
- ✅ Protection Fail2Ban (optionnel) / Fail2Ban protection (optional)

**Prérequis / Prerequisites:**
- Nom de domaine pointant vers votre VPS / Domain name pointing to your VPS
- Ports 80 et 443 ouverts / Ports 80 and 443 open
- Adresse email pour Let's Encrypt / Email address for Let's Encrypt

## 📊 Zabbix Monitoring / Monitoring Zabbix

### Installation Rapide / Quick Installation

```bash
# Installation automatique / Automatic installation
bash setup-zabbix.sh

# Ou installation manuelle / Or manual installation
mkdir -p ~/zabbix-docker
cd ~/zabbix-docker
cp zabbix-docker-compose.yml docker-compose.yml
cp zabbix-env.example .env
nano .env  # Modifier les configurations / Edit configurations
docker compose up -d

# Accès / Access
# http://localhost:8080
```

### Identifiants Par Défaut / Default Credentials
- Username / Utilisateur: `Admin` (avec A majuscule / capital A)
- Password / Mot de passe: `zabbix`
- **⚠️ IMPORTANT:** Changez le mot de passe immédiatement! / Change password immediately!

### Ce que vous pouvez monitorer / What you can monitor
- ✅ Serveurs Linux et Windows / Linux and Windows servers
- ✅ Équipements réseau (SNMP) / Network equipment (SNMP)
- ✅ Applications et bases de données / Applications and databases
- ✅ Conteneurs Docker / Docker containers
- ✅ Services cloud (AWS, Azure, GCP)
- ✅ NetBox lui-même / NetBox itself
- ✅ Métriques personnalisées / Custom metrics
- ✅ Alertes en temps réel / Real-time alerts

## 🤖 AWX Automation / Automatisation AWX

### Installation Rapide / Quick Installation

```bash
# Installation automatique / Automatic installation
bash setup-awx.sh

# Ou installation manuelle / Or manual installation
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl

# Start Minikube and deploy AWX
minikube start --cpus=4 --memory=8192
kubectl create namespace awx
kubectl apply -f https://raw.githubusercontent.com/ansible/awx-operator/devel/deploy/awx-operator.yaml -n awx
kubectl apply -f awx-instance.yaml -n awx

# Access / Accès
# http://localhost:30080
```

### Identifiants Par Défaut / Default Credentials
- Username / Utilisateur: `admin`
- Password / Mot de passe: (généré automatiquement / auto-generated - check awx-credentials.txt)
- **⚠️ IMPORTANT:** Sauvegardez le mot de passe en lieu sûr! / Save password securely!

### Ce que vous pouvez automatiser / What you can automate
- ✅ Configuration de serveurs / Server configuration
- ✅ Déploiement d'applications / Application deployment
- ✅ Gestion des patchs / Patch management
- ✅ Provisioning d'infrastructure / Infrastructure provisioning
- ✅ Conformité et audit / Compliance and audit
- ✅ Orchestration multi-cloud / Multi-cloud orchestration
- ✅ CI/CD pipelines
- ✅ Intégration NetBox (inventaires dynamiques) / NetBox integration (dynamic inventories)

## 🔗 Intégrations / Integrations

### NetBox ↔ Zabbix Integration

Synchronisez automatiquement vos devices NetBox avec Zabbix pour le monitoring:
Automatically synchronize your NetBox devices with Zabbix for monitoring:

```bash
# Installation des dépendances / Install dependencies
cd integration-scripts
pip install -r requirements.txt

# Configuration / Configure
cp .env.example .env
nano .env  # Modifier avec vos valeurs / Update with your values

# Exécution / Run
python3 netbox_to_zabbix_sync.py
```

**Guide complet / Full guide:** [NETBOX_ZABBIX_INTEGRATION.md](NETBOX_ZABBIX_INTEGRATION.md)

**Bénéfices / Benefits:**
- ✅ NetBox comme source de vérité / NetBox as source of truth
- ✅ Synchronisation automatique des hôtes / Automatic host synchronization
- ✅ Organisation par sites et tags / Organization by sites and tags
- ✅ Pas de double saisie / No duplicate data entry
- ✅ Cohérence garantie / Guaranteed consistency

### NetBox ↔ AWX Integration

Utilisez NetBox comme inventaire dynamique pour AWX:
Use NetBox as dynamic inventory for AWX:

1. Dans AWX, créez des credentials NetBox / In AWX, create NetBox credentials
2. Ajoutez une source d'inventaire NetBox / Add NetBox inventory source
3. Synchronisez automatiquement / Synchronize automatically
4. Exécutez vos playbooks sur l'infrastructure NetBox / Run playbooks on NetBox infrastructure

**Guide complet / Full guide:** [AWX_MINIKUBE_SETUP.md](AWX_MINIKUBE_SETUP.md#étape-10--intégration-avec-netbox--netbox-integration)

## 📋 Features / Fonctionnalités

### NetBox v4.4.7 Services / Services NetBox v4.4.7
- ✅ NetBox v4.4.7 Web Application (latest stable - Nov 2025)
- ✅ PostgreSQL 15 Database
- ✅ Redis Cache & Message Queue (dual Redis setup)
- ✅ Background Workers (RQ Worker for async tasks)
- ✅ Housekeeping Tasks (automated maintenance)
- ✅ Health Checks (all services monitored)
- ✅ Persistent Storage (Docker volumes)
- ✅ GraphQL API Support (new in v4.x)
- ✅ Modern UI & Enhanced Dashboards
- ✅ OAuth2/SAML Authentication
- ✅ Python 3.8-3.12 Support

### Zabbix 7.0 LTS Services / Services Zabbix 7.0 LTS
- ✅ Zabbix Server 7.0 LTS (long-term support)
- ✅ PostgreSQL 15 Database
- ✅ Zabbix Web Interface (Nginx-based)
- ✅ Zabbix Agent (self-monitoring)
- ✅ SNMP Traps Support
- ✅ Real-time Monitoring & Alerting
- ✅ Auto-discovery
- ✅ Custom Dashboards & Widgets
- ✅ REST API
- ✅ Email/SMS/Webhook Notifications
- ✅ Pre-configured Templates (Linux, Windows, Network, Cloud)
- ✅ Performance Metrics & Trending

### AWX (Ansible Tower) Services / Services AWX
- ✅ AWX Web Interface (modern UI)
- ✅ Minikube (Kubernetes cluster)
- ✅ AWX Operator (automatic management)
- ✅ PostgreSQL Database
- ✅ Job Execution Engine
- ✅ Dynamic Inventories (NetBox, AWS, Azure, VMware, etc.)
- ✅ Role-Based Access Control (RBAC)
- ✅ Workflow Engine
- ✅ REST API & CLI
- ✅ Git Integration
- ✅ Credential Management (Vault support)
- ✅ Job Templates & Scheduling
- ✅ Real-time Job Monitoring
- ✅ Audit Logging

## 🛠️ Prerequisites / Prérequis

- Ubuntu 20.04+ or similar Linux distribution / Ubuntu 20.04+ ou distribution Linux similaire
- 2GB+ RAM minimum / 2 Go+ RAM minimum
- 10GB+ disk space / 10 Go+ d'espace disque
- Internet connection / Connexion Internet
- Sudo access / Accès sudo

## 📖 Documentation Links / Liens Documentation

### NetBox
- [NetBox Official Documentation](https://docs.netbox.dev/)
- [NetBox Docker Repository](https://github.com/netbox-community/netbox-docker)
- [NetBox Community](https://github.com/netbox-community/netbox/discussions)

### Zabbix
- [Zabbix Official Documentation](https://www.zabbix.com/documentation/7.0/)
- [Zabbix Docker Repository](https://github.com/zabbix/zabbix-docker)
- [Zabbix Community Templates](https://www.zabbix.com/integrations)
- [Zabbix Forum](https://www.zabbix.com/forum/)

### AWX
- [AWX Official Documentation](https://ansible.readthedocs.io/projects/awx/en/latest/)
- [AWX GitHub Repository](https://github.com/ansible/awx)
- [AWX Operator GitHub](https://github.com/ansible/awx-operator)
- [Ansible Documentation](https://docs.ansible.com/)

### Kubernetes & Minikube
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Documentation](https://kubernetes.io/docs/reference/kubectl/)

### Docker
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🤝 Contributing / Contribuer

Contributions are welcome! / Les contributions sont les bienvenues!

## 📝 License / Licence

This project documentation is provided as-is for educational purposes.
Cette documentation de projet est fournie telle quelle à des fins éducatives.