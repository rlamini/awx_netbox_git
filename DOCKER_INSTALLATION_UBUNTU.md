# Guide d'Installation Docker sur Ubuntu / Docker Installation Guide for Ubuntu

## 📋 Prérequis / Prerequisites

- Ubuntu 20.04 LTS, 22.04 LTS, ou version ultérieure / or later
- Accès sudo / sudo access
- Connexion Internet / Internet connection

## 🚀 Étape 1 : Mettre à jour le système / Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

## 🧹 Étape 2 : Supprimer les anciennes versions (optionnel) / Step 2: Remove Old Versions (Optional)

```bash
sudo apt remove docker docker-engine docker.io containerd runc
```

## 📦 Étape 3 : Installer les dépendances / Step 3: Install Dependencies

```bash
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

## 🔑 Étape 4 : Ajouter la clé GPG officielle de Docker / Step 4: Add Docker's Official GPG Key

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

## 📝 Étape 5 : Configurer le dépôt Docker / Step 5: Set Up Docker Repository

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

## ⚙️ Étape 6 : Installer Docker Engine / Step 6: Install Docker Engine

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## ✅ Étape 7 : Vérifier l'installation / Step 7: Verify Installation

```bash
sudo docker --version
sudo docker compose version
```

## 👤 Étape 8 : Ajouter votre utilisateur au groupe Docker / Step 8: Add User to Docker Group

Pour exécuter Docker sans sudo / To run Docker without sudo:

```bash
sudo usermod -aG docker $USER
```

**Important:** Déconnectez-vous et reconnectez-vous pour appliquer les changements, ou utilisez:
**Important:** Log out and log back in for changes to take effect, or use:

```bash
newgrp docker
```

## 🧪 Étape 9 : Tester Docker / Step 9: Test Docker

```bash
docker run hello-world
```

Si vous voyez "Hello from Docker!", l'installation est réussie! 🎉
If you see "Hello from Docker!", the installation is successful! 🎉

## 🔄 Étape 10 : Activer Docker au démarrage / Step 10: Enable Docker on Boot

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

## 📊 Commandes Docker utiles / Useful Docker Commands

```bash
# Vérifier le statut / Check status
sudo systemctl status docker

# Lister les conteneurs en cours d'exécution / List running containers
docker ps

# Lister toutes les images / List all images
docker images

# Lister tous les conteneurs / List all containers
docker ps -a

# Arrêter tous les conteneurs / Stop all containers
docker stop $(docker ps -aq)

# Supprimer tous les conteneurs / Remove all containers
docker rm $(docker ps -aq)

# Nettoyer le système / Clean up system
docker system prune -a
```

## 🛠️ Dépannage / Troubleshooting

### Problème de permissions / Permission Issues
Si vous obtenez "permission denied":
```bash
sudo chmod 666 /var/run/docker.sock
```

### Docker ne démarre pas / Docker Won't Start
```bash
sudo systemctl restart docker
sudo journalctl -u docker
```

## 📚 Ressources / Resources

- [Documentation officielle Docker](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
