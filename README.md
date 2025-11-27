# AWX & NetBox v4.4.7 Docker Installation Guide

Guides d'installation complètes pour Docker, NetBox v4.4.7 et AWX avec Docker Compose.
Complete installation guides for Docker, NetBox v4.4.7, and AWX with Docker Compose.

## 📚 Documentation / Documentation

### 🐳 Docker Installation / Installation Docker
- **[DOCKER_INSTALLATION_UBUNTU.md](DOCKER_INSTALLATION_UBUNTU.md)** - Guide complet d'installation de Docker sur Ubuntu / Complete Docker installation guide for Ubuntu

### 📦 NetBox v4.4.7 Installation / Installation NetBox v4.4.7
- **[NETBOX_DOCKER_SETUP.md](NETBOX_DOCKER_SETUP.md)** - Guide d'installation et configuration de NetBox v4.4.7 / NetBox v4.4.7 installation and configuration guide
- **[NETBOX_V4_FEATURES.md](NETBOX_V4_FEATURES.md)** - Nouveautés et fonctionnalités de NetBox v4.x / NetBox v4.x features and what's new
- **[docker-compose.yml](docker-compose.yml)** - Fichier Docker Compose complet pour NetBox / Complete Docker Compose file for NetBox
- **[env.example](env.example)** - Exemple de configuration d'environnement / Environment configuration example

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

## 🛠️ Prerequisites / Prérequis

- Ubuntu 20.04+ or similar Linux distribution / Ubuntu 20.04+ ou distribution Linux similaire
- 2GB+ RAM minimum / 2 Go+ RAM minimum
- 10GB+ disk space / 10 Go+ d'espace disque
- Internet connection / Connexion Internet
- Sudo access / Accès sudo

## 📖 Documentation Links / Liens Documentation

- [NetBox Official Documentation](https://docs.netbox.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [NetBox Docker Repository](https://github.com/netbox-community/netbox-docker)

## 🤝 Contributing / Contribuer

Contributions are welcome! / Les contributions sont les bienvenues!

## 📝 License / Licence

This project documentation is provided as-is for educational purposes.
Cette documentation de projet est fournie telle quelle à des fins éducatives.