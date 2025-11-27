# Guide d'Installation NetBox avec Docker / NetBox Docker Installation Guide

## 📋 Qu'est-ce que NetBox? / What is NetBox?

NetBox est une application web open-source de gestion d'infrastructure réseau et de DCIM (Data Center Infrastructure Management). Il permet de documenter et gérer:
- Réseaux IP (IPAM)
- Racks et équipements
- Connexions et câblage
- Circuits et fournisseurs
- Et bien plus encore!

NetBox is an open-source web application for network infrastructure management and DCIM. It helps document and manage networks, racks, equipment, connections, circuits, and more.

## 🔧 Prérequis / Prerequisites

- Docker et Docker Compose installés (voir DOCKER_INSTALLATION_UBUNTU.md)
- Au moins 2 Go de RAM disponible / At least 2GB RAM available
- 10 Go d'espace disque / 10GB disk space
- Accès sudo / sudo access

## 📁 Étape 1 : Créer la structure du projet / Step 1: Create Project Structure

```bash
# Créer le répertoire principal / Create main directory
mkdir -p ~/netbox-docker
cd ~/netbox-docker

# Créer les sous-répertoires / Create subdirectories
mkdir -p postgres-data redis-data netbox-media netbox-reports netbox-scripts
```

## 📋 Étape 2 : Créer le fichier docker-compose.yml / Step 2: Create docker-compose.yml

Créez le fichier `docker-compose.yml` (voir le fichier dans ce dépôt).
Create the `docker-compose.yml` file (see the file in this repository).

```bash
# Copier le fichier depuis ce dépôt / Copy the file from this repository
cp docker-compose.yml ~/netbox-docker/
```

## 🔐 Étape 3 : Créer le fichier .env / Step 3: Create .env File

Créez un fichier `.env` avec vos configurations:
Create a `.env` file with your configurations:

```bash
nano .env
```

Copiez le contenu du fichier `env.example` fourni dans ce dépôt.
Copy the content from the `env.example` file provided in this repository.

**Important:** Modifiez les valeurs suivantes / Change the following values:
- `SECRET_KEY` : Générez une clé aléatoire / Generate a random key
- `SUPERUSER_PASSWORD` : Votre mot de passe admin / Your admin password
- `DB_PASSWORD` : Mot de passe PostgreSQL / PostgreSQL password

### Générer une clé secrète / Generate a Secret Key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Ou / Or:

```bash
openssl rand -base64 48
```

## 🚀 Étape 4 : Démarrer NetBox / Step 4: Start NetBox

```bash
cd ~/netbox-docker

# Télécharger les images / Pull images
docker compose pull

# Démarrer les services en arrière-plan / Start services in background
docker compose up -d

# Vérifier les logs / Check logs
docker compose logs -f
```

## ⏳ Étape 5 : Attendre l'initialisation / Step 5: Wait for Initialization

La première exécution peut prendre 2-5 minutes. Vérifiez que tous les conteneurs sont en cours d'exécution:
The first run may take 2-5 minutes. Check that all containers are running:

```bash
docker compose ps
```

Tous les services doivent afficher "Up" / All services should show "Up".

## 👤 Étape 6 : Créer le super utilisateur / Step 6: Create Superuser

Si vous n'avez pas configuré les variables SUPERUSER dans .env:
If you haven't configured SUPERUSER variables in .env:

```bash
docker compose exec netbox python /opt/netbox/netbox/manage.py createsuperuser
```

## 🌐 Étape 7 : Accéder à NetBox / Step 7: Access NetBox

Ouvrez votre navigateur et accédez à:
Open your browser and navigate to:

```
http://localhost:8000
```

Ou si vous êtes sur un serveur distant / Or if on a remote server:
```
http://YOUR_SERVER_IP:8000
```

**Identifiants par défaut / Default credentials:**
- Utilisateur / Username: `admin`
- Mot de passe / Password: celui défini dans .env / the one set in .env

## 🔧 Commandes utiles / Useful Commands

### Arrêter NetBox / Stop NetBox
```bash
docker compose stop
```

### Démarrer NetBox / Start NetBox
```bash
docker compose start
```

### Redémarrer NetBox / Restart NetBox
```bash
docker compose restart
```

### Voir les logs / View logs
```bash
# Tous les services / All services
docker compose logs -f

# Service spécifique / Specific service
docker compose logs -f netbox
docker compose logs -f postgres
docker compose logs -f redis
```

### Mettre à jour NetBox / Update NetBox
```bash
docker compose pull
docker compose up -d
```

### Sauvegarder la base de données / Backup Database
```bash
docker compose exec -T postgres pg_dump -U netbox netbox > netbox_backup_$(date +%Y%m%d).sql
```

### Restaurer la base de données / Restore Database
```bash
docker compose exec -T postgres psql -U netbox netbox < netbox_backup_YYYYMMDD.sql
```

### Accéder au shell NetBox / Access NetBox Shell
```bash
docker compose exec netbox python /opt/netbox/netbox/manage.py shell
```

### Exécuter des migrations / Run Migrations
```bash
docker compose exec netbox python /opt/netbox/netbox/manage.py migrate
```

## 📊 Configuration avancée / Advanced Configuration

### Reverse Proxy avec Nginx

Pour exposer NetBox sur le port 80/443 avec SSL:
To expose NetBox on port 80/443 with SSL:

```bash
# Installer Nginx / Install Nginx
sudo apt install nginx

# Créer la configuration / Create configuration
sudo nano /etc/nginx/sites-available/netbox
```

Exemple de configuration Nginx / Nginx configuration example:

```nginx
server {
    listen 80;
    server_name netbox.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activer le site / Enable site
sudo ln -s /etc/nginx/sites-available/netbox /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Configurer SSL avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d netbox.example.com
```

## 🛠️ Dépannage / Troubleshooting

### NetBox ne démarre pas / NetBox Won't Start

```bash
# Vérifier les logs / Check logs
docker compose logs netbox

# Vérifier l'état des conteneurs / Check container status
docker compose ps
```

### Erreur de connexion à la base de données / Database Connection Error

```bash
# Redémarrer PostgreSQL / Restart PostgreSQL
docker compose restart postgres

# Attendre 30 secondes puis redémarrer NetBox / Wait 30s then restart NetBox
docker compose restart netbox
```

### Problèmes de permissions / Permission Issues

```bash
# Corriger les permissions des volumes / Fix volume permissions
sudo chown -R 999:999 postgres-data/
sudo chown -R 101:101 netbox-media/ netbox-reports/ netbox-scripts/
```

### Réinitialiser complètement / Complete Reset

⚠️ **Attention: Cela supprimera toutes les données! / Warning: This will delete all data!**

```bash
docker compose down -v
rm -rf postgres-data/* redis-data/* netbox-media/* netbox-reports/* netbox-scripts/*
docker compose up -d
```

## 📚 Prochaines étapes / Next Steps

1. **Importer des données** / Import data
2. **Configurer les utilisateurs et permissions** / Configure users and permissions
3. **Personnaliser les champs et modèles** / Customize fields and templates
4. **Intégrer avec vos outils existants** / Integrate with existing tools
5. **Mettre en place des sauvegardes automatiques** / Set up automatic backups

## 🔗 Ressources / Resources

- [Documentation NetBox](https://docs.netbox.dev/)
- [NetBox GitHub](https://github.com/netbox-community/netbox)
- [NetBox Docker GitHub](https://github.com/netbox-community/netbox-docker)
- [Communauté NetBox](https://github.com/netbox-community/netbox/discussions)

## 💡 Conseils / Tips

- Sauvegardez régulièrement votre base de données / Backup your database regularly
- Surveillez l'utilisation des ressources / Monitor resource usage
- Mettez à jour NetBox régulièrement / Update NetBox regularly
- Documentez vos configurations personnalisées / Document custom configurations
- Utilisez des tags et des champs personnalisés / Use tags and custom fields
