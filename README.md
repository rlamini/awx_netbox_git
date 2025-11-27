# AWX & NetBox Docker Installation Guide

Guides d'installation complètes pour Docker, NetBox et AWX avec Docker Compose.
Complete installation guides for Docker, NetBox, and AWX with Docker Compose.

## 📚 Documentation / Documentation

### 🐳 Docker Installation / Installation Docker
- **[DOCKER_INSTALLATION_UBUNTU.md](DOCKER_INSTALLATION_UBUNTU.md)** - Guide complet d'installation de Docker sur Ubuntu / Complete Docker installation guide for Ubuntu

### 📦 NetBox Installation / Installation NetBox
- **[NETBOX_DOCKER_SETUP.md](NETBOX_DOCKER_SETUP.md)** - Guide d'installation et configuration de NetBox / NetBox installation and configuration guide
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

### NetBox Services / Services NetBox
- ✅ NetBox Web Application
- ✅ PostgreSQL Database
- ✅ Redis Cache & Message Queue
- ✅ Background Workers
- ✅ Housekeeping Tasks
- ✅ Health Checks
- ✅ Persistent Storage

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