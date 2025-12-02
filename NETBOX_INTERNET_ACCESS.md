# Guide d'Accès NetBox via Internet / NetBox Internet Access Guide

## 🌐 Aperçu / Overview

Ce guide vous montre comment exposer NetBox sur Internet de manière sécurisée depuis votre VPS cloud avec:
- Nginx comme reverse proxy
- SSL/HTTPS avec Let's Encrypt (gratuit)
- Configuration du pare-feu
- Sécurisation de NetBox

This guide shows how to securely expose NetBox to the Internet from your cloud VPS with Nginx reverse proxy, free SSL/HTTPS, firewall configuration, and NetBox hardening.

## ⚠️ Prérequis / Prerequisites

### 1. Nom de Domaine / Domain Name
Vous avez besoin d'un nom de domaine pointant vers votre VPS:
- Exemple: `netbox.votredomaine.com` ou `netbox.example.com`
- Le DNS doit pointer vers l'IP publique de votre VPS

You need a domain name pointing to your VPS public IP.

### 2. VPS avec IP Publique / VPS with Public IP
- Ubuntu 20.04+ recommandé
- Ports 80 et 443 ouverts
- Accès root ou sudo

### 3. NetBox Installé / NetBox Installed
- NetBox fonctionnel sur `http://localhost:8000`
- Suivre d'abord [NETBOX_DOCKER_SETUP.md](NETBOX_DOCKER_SETUP.md)

## 📋 Architecture

```
Internet
   ↓
[Port 443 HTTPS]
   ↓
Nginx (Reverse Proxy + SSL)
   ↓
[Port 8000]
   ↓
NetBox Docker Container
```

## 🚀 Installation Étape par Étape / Step-by-Step Installation

### Étape 1 : Installer Nginx / Step 1: Install Nginx

```bash
# Mettre à jour le système / Update system
sudo apt update
sudo apt upgrade -y

# Installer Nginx / Install Nginx
sudo apt install nginx -y

# Vérifier que Nginx fonctionne / Verify Nginx is running
sudo systemctl status nginx
sudo systemctl enable nginx
```

### Étape 2 : Configurer le Pare-feu / Step 2: Configure Firewall

```bash
# Si vous utilisez UFW / If using UFW
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status

# Vérifier les ports ouverts / Check open ports
sudo ss -tulpn | grep LISTEN
```

**Ports requis / Required ports:**
- Port 22 (SSH) - pour l'administration
- Port 80 (HTTP) - pour Let's Encrypt et redirection
- Port 443 (HTTPS) - pour l'accès sécurisé

### Étape 3 : Créer la Configuration Nginx / Step 3: Create Nginx Configuration

```bash
# Créer le fichier de configuration / Create config file
sudo nano /etc/nginx/sites-available/netbox
```

**Copiez cette configuration (remplacez `netbox.example.com` par votre domaine):**

```nginx
# NetBox Nginx Configuration
# Replace netbox.example.com with your actual domain

upstream netbox {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    listen [::]:80;

    server_name netbox.example.com;

    # Redirect HTTP to HTTPS (will be enabled after SSL setup)
    # return 301 https://$server_name$request_uri;

    # Temporary: Allow HTTP for Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Proxy to NetBox
    location / {
        proxy_pass http://netbox;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;

        # Increase timeouts for long-running requests
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Serve static files (optional, for better performance)
    location /static/ {
        alias /opt/netbox/netbox/static/;
    }

    # Increase max upload size
    client_max_body_size 25m;
}

# HTTPS server (will be configured by Certbot)
# server {
#     listen 443 ssl http2;
#     listen [::]:443 ssl http2;
#
#     server_name netbox.example.com;
#
#     # SSL certificates (Let's Encrypt will add these)
#     # ssl_certificate /etc/letsencrypt/live/netbox.example.com/fullchain.pem;
#     # ssl_certificate_key /etc/letsencrypt/live/netbox.example.com/privkey.pem;
#
#     # Rest of configuration same as above
# }
```

**Sauvegardez et activez la configuration:**

```bash
# Activer le site / Enable site
sudo ln -s /etc/nginx/sites-available/netbox /etc/nginx/sites-enabled/

# Supprimer la config par défaut / Remove default config
sudo rm /etc/nginx/sites-enabled/default

# Tester la configuration / Test configuration
sudo nginx -t

# Recharger Nginx / Reload Nginx
sudo systemctl reload nginx
```

### Étape 4 : Vérifier l'Accès HTTP / Step 4: Verify HTTP Access

Testez l'accès à NetBox via votre domaine:
```
http://netbox.example.com
```

Vous devriez voir l'interface NetBox.

### Étape 5 : Installer Certbot pour SSL / Step 5: Install Certbot for SSL

```bash
# Installer Certbot et le plugin Nginx / Install Certbot with Nginx plugin
sudo apt install certbot python3-certbot-nginx -y

# Obtenir un certificat SSL gratuit / Get free SSL certificate
sudo certbot --nginx -d netbox.example.com

# Suivre les instructions interactives:
# 1. Entrer votre email
# 2. Accepter les conditions
# 3. Choisir de rediriger HTTP vers HTTPS (recommandé)
```

**Certbot va automatiquement:**
- Générer un certificat SSL gratuit
- Configurer Nginx pour HTTPS
- Configurer le renouvellement automatique

### Étape 6 : Vérifier le Renouvellement Automatique / Step 6: Verify Auto-Renewal

```bash
# Tester le renouvellement / Test renewal
sudo certbot renew --dry-run

# Vérifier le timer systemd / Check systemd timer
sudo systemctl status certbot.timer
```

Le certificat se renouvellera automatiquement tous les 90 jours.

### Étape 7 : Accéder à NetBox via HTTPS / Step 7: Access NetBox via HTTPS

Votre NetBox est maintenant accessible de manière sécurisée:
```
https://netbox.example.com
```

## 🔒 Sécurisation de NetBox / NetBox Security Hardening

### 1. Mettre à Jour le Fichier .env / Update .env File

```bash
cd ~/netbox-docker
nano .env
```

**Modifiez ces paramètres:**

```bash
# Définir votre domaine / Set your domain
ALLOWED_HOSTS=netbox.example.com,localhost

# Désactiver CORS pour tous / Disable CORS for all
CORS_ORIGIN_ALLOW_ALL=False

# Forcer HTTPS (optionnel) / Force HTTPS (optional)
# Décommentez après avoir configuré SSL / Uncomment after SSL setup
# SECURE_SSL_REDIRECT=True
```

**Redémarrer NetBox:**

```bash
docker compose down
docker compose up -d
```

### 2. Configuration Nginx Avancée / Advanced Nginx Configuration

Ajoutez ces directives de sécurité dans votre configuration Nginx:

```bash
sudo nano /etc/nginx/sites-available/netbox
```

**Ajoutez dans le bloc `server` HTTPS:**

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name netbox.example.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/netbox.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/netbox.example.com/privkey.pem;

    # SSL Security Headers
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rest of your configuration...
    location / {
        proxy_pass http://netbox;
        # ... autres directives proxy
    }
}
```

```bash
# Tester et recharger / Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Configurer un Pare-feu Applicatif / Configure Application Firewall

```bash
# Bloquer l'accès direct au port 8000 depuis Internet
# Block direct access to port 8000 from Internet
sudo ufw deny 8000

# Autoriser seulement Nginx / Allow only Nginx
sudo ufw status numbered
```

### 4. Activer Fail2Ban (Protection contre les Attaques) / Enable Fail2Ban

```bash
# Installer Fail2Ban / Install Fail2Ban
sudo apt install fail2ban -y

# Créer une config pour Nginx / Create Nginx config
sudo nano /etc/fail2ban/jail.local
```

**Ajoutez:**

```ini
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
```

```bash
# Démarrer Fail2Ban / Start Fail2Ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo fail2ban-client status
```

## 📊 Monitoring et Logs / Monitoring and Logs

### Vérifier les Logs Nginx / Check Nginx Logs

```bash
# Logs d'accès / Access logs
sudo tail -f /var/log/nginx/access.log

# Logs d'erreur / Error logs
sudo tail -f /var/log/nginx/error.log

# Logs NetBox / NetBox logs
cd ~/netbox-docker
docker compose logs -f netbox
```

### Vérifier l'État des Services / Check Service Status

```bash
# Nginx
sudo systemctl status nginx

# NetBox containers
docker compose ps

# Certificat SSL / SSL certificate
sudo certbot certificates
```

## 🔧 Dépannage / Troubleshooting

### Problème 1: "502 Bad Gateway"

```bash
# Vérifier que NetBox est en cours d'exécution / Check NetBox is running
docker compose ps

# Vérifier les logs / Check logs
docker compose logs netbox

# Redémarrer NetBox / Restart NetBox
docker compose restart
```

### Problème 2: Certificat SSL Non Reconnu / SSL Certificate Not Recognized

```bash
# Forcer le renouvellement / Force renewal
sudo certbot renew --force-renewal

# Vérifier la config Nginx / Check Nginx config
sudo nginx -t
```

### Problème 3: Impossible d'Accéder au Site / Cannot Access Site

```bash
# Vérifier le DNS / Check DNS
nslookup netbox.example.com

# Vérifier le pare-feu / Check firewall
sudo ufw status

# Ping le serveur / Ping server
ping netbox.example.com
```

### Problème 4: NetBox Lent / NetBox Slow

```bash
# Augmenter les ressources Docker / Increase Docker resources
# Modifier docker-compose.yml pour ajouter des limites

# Vérifier l'utilisation des ressources / Check resource usage
docker stats

# Optimiser PostgreSQL
docker compose exec postgres psql -U netbox -c "VACUUM ANALYZE;"
```

## 📱 Accès Mobile / Mobile Access

NetBox v4.4.7 est responsive et fonctionne bien sur mobile:
- Interface adaptée aux smartphones
- Touch-friendly
- Performance optimisée

## 🔐 Bonnes Pratiques de Sécurité / Security Best Practices

### ✅ À Faire / Do's:
1. ✅ Toujours utiliser HTTPS (SSL/TLS)
2. ✅ Changer le mot de passe admin par défaut
3. ✅ Utiliser des mots de passe forts
4. ✅ Activer l'authentification à deux facteurs (2FA)
5. ✅ Mettre à jour régulièrement NetBox
6. ✅ Surveiller les logs d'accès
7. ✅ Sauvegarder régulièrement la base de données
8. ✅ Limiter l'accès par IP si possible (whitelist)
9. ✅ Utiliser OAuth2/SAML pour les entreprises
10. ✅ Activer les audits de sécurité

### ❌ À Ne Pas Faire / Don'ts:
1. ❌ N'exposez jamais le port 8000 directement
2. ❌ Ne pas utiliser HTTP (sans SSL)
3. ❌ Ne pas utiliser le mot de passe par défaut
4. ❌ Ne pas désactiver les mises à jour de sécurité
5. ❌ Ne pas ignorer les alertes de sécurité

## 🌍 Configuration Avancée: Restriction par IP / IP Whitelisting

Si vous voulez limiter l'accès à certaines IPs:

```nginx
# Dans /etc/nginx/sites-available/netbox
server {
    # ... votre configuration SSL

    # Autoriser seulement certaines IPs / Allow only specific IPs
    allow 203.0.113.0/24;    # Votre réseau bureau / Your office network
    allow 198.51.100.50;      # Votre IP maison / Your home IP
    deny all;                 # Bloquer tout le reste / Block everything else

    location / {
        proxy_pass http://netbox;
        # ... reste de la config
    }
}
```

## 📈 Performance: CDN et Caching / CDN and Caching

Pour améliorer les performances globales:

```nginx
# Cache statique / Static caching
location /static/ {
    alias /opt/netbox/netbox/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Compression Gzip
gzip on;
gzip_vary on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

## 🔄 Sauvegarde et Restauration / Backup and Restore

### Sauvegarde Automatique / Automated Backup

```bash
# Créer un script de sauvegarde / Create backup script
sudo nano /usr/local/bin/netbox-backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backup/netbox"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Sauvegarder la base de données / Backup database
docker compose -f ~/netbox-docker/docker-compose.yml exec -T postgres \
    pg_dump -U netbox netbox | gzip > $BACKUP_DIR/netbox_db_$DATE.sql.gz

# Garder seulement les 7 derniers jours / Keep only last 7 days
find $BACKUP_DIR -name "netbox_db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: netbox_db_$DATE.sql.gz"
```

```bash
# Rendre exécutable / Make executable
sudo chmod +x /usr/local/bin/netbox-backup.sh

# Ajouter au crontab (sauvegarde quotidienne à 2h du matin)
sudo crontab -e
# Ajouter cette ligne / Add this line:
0 2 * * * /usr/local/bin/netbox-backup.sh
```

## 📞 Support et Ressources / Support and Resources

- [NetBox Documentation](https://docs.netbox.dev/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [NetBox Community](https://github.com/netbox-community/netbox/discussions)

## ✅ Checklist Finale / Final Checklist

Avant de mettre en production / Before going to production:

- [ ] DNS configuré et pointant vers le VPS
- [ ] Nginx installé et configuré
- [ ] Certificat SSL actif (HTTPS fonctionne)
- [ ] Pare-feu configuré (ports 80, 443 ouverts)
- [ ] ALLOWED_HOSTS configuré dans .env
- [ ] Mot de passe admin changé
- [ ] Fail2Ban activé
- [ ] Sauvegarde automatique configurée
- [ ] Logs surveillés
- [ ] Tests d'accès effectués depuis Internet
- [ ] Documentation créée pour votre équipe

---

🎉 **Félicitations!** Votre NetBox est maintenant accessible de manière sécurisée depuis Internet!

🎉 **Congratulations!** Your NetBox is now securely accessible from the Internet!
