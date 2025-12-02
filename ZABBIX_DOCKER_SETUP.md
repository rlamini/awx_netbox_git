# Guide d'Installation Zabbix avec Docker / Zabbix Docker Installation Guide

## 📋 Qu'est-ce que Zabbix? / What is Zabbix?

Zabbix est une solution de monitoring open-source de niveau entreprise pour surveiller:
- Serveurs et équipements réseau / Servers and network equipment
- Applications et services / Applications and services
- Cloud et conteneurs / Cloud and containers
- Performance et disponibilité / Performance and availability
- Métriques et alertes en temps réel / Real-time metrics and alerts

Zabbix is an enterprise-class open-source monitoring solution for networks, servers, applications, cloud, and containers with real-time metrics and alerts.

## 🆕 Zabbix 7.0 LTS - Dernière Version / Latest Version

Zabbix 7.0 LTS est la dernière version stable avec support long terme (LTS):
- 🚀 Interface utilisateur modernisée
- 📊 Nouveaux tableaux de bord et widgets
- 🔌 API REST améliorée
- 🤖 Auto-découverte avancée
- 📈 Meilleures performances
- 🔒 Sécurité renforcée
- 🌐 Support multi-tenant amélioré

Zabbix 7.0 LTS is the latest stable release with long-term support, featuring modern UI, enhanced dashboards, improved REST API, advanced auto-discovery, better performance, and enhanced security.

## 🔧 Prérequis / Prerequisites

- Docker et Docker Compose installés (voir DOCKER_INSTALLATION_UBUNTU.md)
- Au moins 2 Go de RAM disponible / At least 2GB RAM available
- 10 Go d'espace disque / 10GB disk space
- Accès sudo / sudo access

## 📁 Étape 1 : Créer la structure du projet / Step 1: Create Project Structure

```bash
# Créer le répertoire principal / Create main directory
mkdir -p ~/zabbix-docker
cd ~/zabbix-docker

# Créer les sous-répertoires / Create subdirectories
mkdir -p postgres-data zabbix-scripts zabbix-modules
```

## 📋 Étape 2 : Créer le fichier docker-compose.yml / Step 2: Create docker-compose.yml

Créez le fichier `docker-compose.yml` (voir le fichier dans ce dépôt).
Create the `docker-compose.yml` file (see the file in this repository).

```bash
# Copier le fichier depuis ce dépôt / Copy the file from this repository
cp zabbix-docker-compose.yml ~/zabbix-docker/docker-compose.yml
```

## 🔐 Étape 3 : Créer le fichier .env / Step 3: Create .env File

Créez un fichier `.env` avec vos configurations:
Create a `.env` file with your configurations:

```bash
nano .env
```

Copiez le contenu du fichier `zabbix-env.example` fourni dans ce dépôt.
Copy the content from the `zabbix-env.example` file provided in this repository.

**Important:** Modifiez les valeurs suivantes / Change the following values:
- `POSTGRES_PASSWORD` : Mot de passe PostgreSQL / PostgreSQL password
- `ZABBIX_ADMIN_PASSWORD` : Mot de passe admin Zabbix / Zabbix admin password

## 🚀 Étape 4 : Démarrer Zabbix / Step 4: Start Zabbix

```bash
cd ~/zabbix-docker

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

## 🌐 Étape 6 : Accéder à Zabbix / Step 6: Access Zabbix

Ouvrez votre navigateur et accédez à:
Open your browser and navigate to:

```
http://localhost:8080
```

Ou si vous êtes sur un serveur distant / Or if on a remote server:
```
http://YOUR_SERVER_IP:8080
```

## 👤 Étape 7 : Connexion Initiale / Step 7: Initial Login

**Identifiants par défaut / Default credentials:**
- Utilisateur / Username: `Admin` (avec A majuscule / capital A)
- Mot de passe / Password: `zabbix` (ou celui configuré dans .env / or as configured in .env)

**Important:** Changez le mot de passe admin immédiatement après la première connexion!
**Important:** Change the admin password immediately after first login!

## 🔧 Commandes utiles / Useful Commands

### Arrêter Zabbix / Stop Zabbix
```bash
docker compose stop
```

### Démarrer Zabbix / Start Zabbix
```bash
docker compose start
```

### Redémarrer Zabbix / Restart Zabbix
```bash
docker compose restart
```

### Voir les logs / View logs
```bash
# Tous les services / All services
docker compose logs -f

# Service spécifique / Specific service
docker compose logs -f zabbix-server
docker compose logs -f zabbix-web
docker compose logs -f postgres
```

### Mettre à jour Zabbix / Update Zabbix
```bash
docker compose pull
docker compose up -d
```

### Sauvegarder la base de données / Backup Database
```bash
docker compose exec -T postgres pg_dump -U zabbix zabbix > zabbix_backup_$(date +%Y%m%d).sql
```

### Restaurer la base de données / Restore Database
```bash
docker compose exec -T postgres psql -U zabbix zabbix < zabbix_backup_YYYYMMDD.sql
```

## 📊 Configuration Initiale / Initial Configuration

### 1. Changer le Mot de Passe Admin / Change Admin Password

1. Connectez-vous avec Admin/zabbix
2. Allez dans **User settings** → **User profile**
3. Cliquez sur **Change password**
4. Entrez un nouveau mot de passe fort

### 2. Configurer les Notifications Email / Configure Email Notifications

1. Allez dans **Administration** → **Media types**
2. Cliquez sur **Email**
3. Configurez votre serveur SMTP:
   - SMTP server: `smtp.gmail.com` (exemple)
   - SMTP server port: `587`
   - SMTP helo: `votredomaine.com`
   - SMTP email: `votre@email.com`
   - Authentification: activée

### 3. Ajouter votre Premier Hôte / Add Your First Host

1. Allez dans **Configuration** → **Hosts**
2. Cliquez sur **Create host**
3. Configurez:
   - Nom de l'hôte / Host name: `Mon Serveur`
   - Groupes / Groups: `Linux servers`
   - Agent interface: IP de votre serveur
   - Templates: `Linux by Zabbix agent`

### 4. Installer Zabbix Agent sur les Hôtes / Install Zabbix Agent on Hosts

```bash
# Sur l'hôte à monitorer / On the host to monitor
wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_7.0-1+ubuntu22.04_all.deb
sudo dpkg -i zabbix-release_7.0-1+ubuntu22.04_all.deb
sudo apt update
sudo apt install zabbix-agent -y

# Configurer l'agent / Configure agent
sudo nano /etc/zabbix/zabbix_agentd.conf

# Modifier ces lignes / Modify these lines:
# Server=IP_DU_SERVEUR_ZABBIX
# ServerActive=IP_DU_SERVEUR_ZABBIX
# Hostname=Mon_Serveur

# Redémarrer l'agent / Restart agent
sudo systemctl restart zabbix-agent
sudo systemctl enable zabbix-agent
```

## 🌐 Exposer Zabbix sur Internet / Expose Zabbix to Internet

Si vous voulez accéder à Zabbix depuis Internet avec SSL/HTTPS:

### Créer la Configuration Nginx / Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/zabbix
```

```nginx
upstream zabbix {
    server 127.0.0.1:8080 fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;

    server_name zabbix.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        proxy_pass http://zabbix;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    client_max_body_size 10m;
}
```

```bash
# Activer le site / Enable site
sudo ln -s /etc/nginx/sites-available/zabbix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Obtenir le certificat SSL / Get SSL certificate
sudo certbot --nginx -d zabbix.example.com
```

## 📊 Tableaux de Bord et Monitoring / Dashboards and Monitoring

### Templates Pré-configurés / Pre-configured Templates

Zabbix inclut des templates pour:
- Linux servers (CPU, RAM, Disk, Network)
- Windows servers
- VMware
- Docker containers
- MySQL, PostgreSQL, MongoDB
- Apache, Nginx
- SNMP devices (switches, routers)
- Cloud services (AWS, Azure, GCP)

### Créer un Tableau de Bord / Create a Dashboard

1. Allez dans **Monitoring** → **Dashboards**
2. Cliquez sur **Create dashboard**
3. Ajoutez des widgets:
   - Graph (graphiques de métriques)
   - Plain text (texte)
   - Problems (problèmes)
   - System information
   - Map (carte réseau)

### Configurer des Alertes / Configure Alerts

1. Allez dans **Configuration** → **Actions**
2. Cliquez sur **Create action**
3. Configurez:
   - Nom: `Alert Email`
   - Conditions: `Trigger severity >= Warning`
   - Operations: Envoyer un email

## 🔌 Intégration avec NetBox / NetBox Integration

Zabbix peut être intégré avec NetBox pour:
- Synchroniser les hôtes automatiquement
- Importer les inventaires
- Mettre à jour les adresses IP

### Script d'Intégration (Optionnel) / Integration Script (Optional)

```python
# Exemple de script Python pour synchroniser NetBox → Zabbix
import requests

NETBOX_URL = "https://netbox.example.com"
NETBOX_TOKEN = "votre_token_netbox"
ZABBIX_URL = "http://localhost:8080/api_jsonrpc.php"
ZABBIX_USER = "Admin"
ZABBIX_PASS = "votre_mot_de_passe"

# Obtenir les devices de NetBox
# Get devices from NetBox
headers = {"Authorization": f"Token {NETBOX_TOKEN}"}
devices = requests.get(f"{NETBOX_URL}/api/dcim/devices/", headers=headers).json()

# Ajouter à Zabbix
# Add to Zabbix
# ... (code de synchronisation)
```

## 🛠️ Dépannage / Troubleshooting

### Zabbix ne démarre pas / Zabbix Won't Start

```bash
# Vérifier les logs / Check logs
docker compose logs zabbix-server

# Vérifier l'état des conteneurs / Check container status
docker compose ps

# Redémarrer tous les services / Restart all services
docker compose restart
```

### Erreur de connexion à la base de données / Database Connection Error

```bash
# Redémarrer PostgreSQL / Restart PostgreSQL
docker compose restart postgres

# Attendre 30 secondes puis redémarrer Zabbix / Wait 30s then restart Zabbix
docker compose restart zabbix-server
```

### Interface Web ne charge pas / Web Interface Not Loading

```bash
# Vérifier que le port 8080 est libre / Check port 8080 is free
sudo ss -tulpn | grep 8080

# Vérifier les logs web / Check web logs
docker compose logs zabbix-web
```

### Agent ne se connecte pas / Agent Not Connecting

```bash
# Sur l'hôte avec l'agent / On host with agent
sudo systemctl status zabbix-agent

# Vérifier la config / Check config
sudo cat /etc/zabbix/zabbix_agentd.conf | grep -E "Server=|Hostname="

# Tester la connexion / Test connection
telnet IP_ZABBIX_SERVER 10051
```

## 📈 Monitoring Recommandé / Recommended Monitoring

### Serveurs Linux / Linux Servers
- CPU utilization
- Memory usage
- Disk space
- Network traffic
- System load
- Processes
- Services status

### Serveurs Windows / Windows Servers
- CPU, RAM, Disk
- Windows services
- Event logs
- Performance counters

### Équipements Réseau / Network Equipment
- SNMP monitoring
- Interface status
- Bandwidth usage
- Errors and discards

### Applications / Applications
- Docker containers
- Databases (PostgreSQL, MySQL, MongoDB)
- Web servers (Nginx, Apache)
- Application logs

### NetBox Integration
- Monitorer NetBox lui-même
- CPU, RAM, Disk de NetBox
- Base de données PostgreSQL
- Performance des requêtes API

## 💡 Bonnes Pratiques / Best Practices

### Configuration

1. ✅ Utilisez des templates pour standardiser
2. ✅ Organisez les hôtes par groupes
3. ✅ Définissez des noms d'hôtes cohérents
4. ✅ Utilisez des macros pour la flexibilité
5. ✅ Documentez vos configurations

### Alertes

1. ✅ Configurez des seuils réalistes
2. ✅ Évitez la sur-alerte (alert fatigue)
3. ✅ Utilisez des dépendances d'alertes
4. ✅ Testez vos notifications
5. ✅ Créez des escalades pour les alertes critiques

### Sécurité

1. ✅ Changez les mots de passe par défaut
2. ✅ Utilisez HTTPS (SSL/TLS)
3. ✅ Limitez l'accès par IP si possible
4. ✅ Activez l'authentification à deux facteurs
5. ✅ Mettez à jour régulièrement
6. ✅ Utilisez des utilisateurs avec privilèges minimaux
7. ✅ Activez les logs d'audit

### Performance

1. ✅ Ajustez les intervalles de collecte
2. ✅ Utilisez le housekeeping pour nettoyer les vieilles données
3. ✅ Optimisez les requêtes de base de données
4. ✅ Utilisez des proxies Zabbix pour les sites distants
5. ✅ Surveillez les performances de Zabbix lui-même

## 📚 Ressources / Resources

- [Zabbix Official Documentation](https://www.zabbix.com/documentation/7.0/)
- [Zabbix Community Templates](https://www.zabbix.com/integrations)
- [Zabbix Docker GitHub](https://github.com/zabbix/zabbix-docker)
- [Zabbix Forum](https://www.zabbix.com/forum/)
- [Zabbix API Documentation](https://www.zabbix.com/documentation/7.0/manual/api)

## 🎓 Prochaines Étapes / Next Steps

Après l'installation:
1. Changez le mot de passe admin
2. Configurez les notifications email
3. Ajoutez vos premiers hôtes
4. Installez les agents Zabbix
5. Créez vos tableaux de bord
6. Configurez les alertes
7. Testez les notifications
8. Documentez votre configuration
9. Planifiez les sauvegardes
10. Intégrez avec NetBox (optionnel)

---

**Zabbix 7.0 LTS** : La solution de monitoring la plus complète! 🎉

**Zabbix 7.0 LTS**: The most comprehensive monitoring solution! 🎉
