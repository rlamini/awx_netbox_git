# Nginx Configuration Files for NetBox

Ce dossier contient les fichiers de configuration Nginx prêts à l'emploi pour NetBox.
This folder contains ready-to-use Nginx configuration files for NetBox.

## 📁 Fichiers / Files

### 1. `netbox-http.conf`
Configuration HTTP de base (avant SSL)
- Utiliser AVANT d'installer le certificat SSL
- Permet à Let's Encrypt de vérifier votre domaine

Basic HTTP configuration (before SSL)
- Use BEFORE installing SSL certificate
- Allows Let's Encrypt to verify your domain

### 2. `netbox-https.conf`
Configuration HTTPS complète avec SSL
- Utiliser APRÈS avoir installé le certificat SSL
- Inclut tous les en-têtes de sécurité
- Redirect HTTP → HTTPS
- Optimisations de performance

Complete HTTPS configuration with SSL
- Use AFTER installing SSL certificate
- Includes all security headers
- HTTP → HTTPS redirect
- Performance optimizations

## 🚀 Installation Rapide / Quick Installation

### Méthode 1 : Script Automatique / Automated Script

```bash
# Exécuter le script d'installation automatique
sudo bash setup-nginx-ssl.sh
```

Le script va automatiquement:
- Installer Nginx
- Configurer le pare-feu
- Installer Certbot
- Obtenir un certificat SSL
- Configurer NetBox

### Méthode 2 : Installation Manuelle / Manual Installation

#### Étape 1 : Installer Nginx

```bash
sudo apt update
sudo apt install nginx -y
```

#### Étape 2 : Copier la configuration HTTP

```bash
# Copier le fichier de configuration
sudo cp netbox-http.conf /etc/nginx/sites-available/netbox

# IMPORTANT: Éditer et remplacer netbox.example.com par votre domaine
sudo nano /etc/nginx/sites-available/netbox

# Activer le site
sudo ln -s /etc/nginx/sites-available/netbox /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Tester et recharger
sudo nginx -t
sudo systemctl reload nginx
```

#### Étape 3 : Installer SSL avec Certbot

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtenir le certificat SSL (remplacer par votre domaine et email)
sudo certbot --nginx -d netbox.example.com --email votre@email.com
```

#### Étape 4 : (Optionnel) Utiliser la configuration HTTPS avancée

```bash
# Sauvegarder la config générée par Certbot
sudo cp /etc/nginx/sites-available/netbox /etc/nginx/sites-available/netbox.certbot

# Copier notre configuration HTTPS optimisée
sudo cp netbox-https.conf /etc/nginx/sites-available/netbox

# IMPORTANT: Éditer et remplacer netbox.example.com par votre domaine
sudo nano /etc/nginx/sites-available/netbox

# Tester et recharger
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Personnalisation / Customization

### Changer le Domaine / Change Domain

Dans les fichiers de configuration, remplacer toutes les occurrences de:
In configuration files, replace all occurrences of:

```nginx
server_name netbox.example.com;
```

Par votre domaine réel / With your actual domain:

```nginx
server_name votre-domaine.com;
```

### Chemins des Certificats SSL / SSL Certificate Paths

Si vos certificats sont ailleurs, modifier:
If your certificates are elsewhere, modify:

```nginx
ssl_certificate /etc/letsencrypt/live/netbox.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/netbox.example.com/privkey.pem;
```

### Limitation par IP / IP Whitelisting

Pour limiter l'accès à certaines IPs, ajouter dans le bloc `server`:
To limit access to specific IPs, add in the `server` block:

```nginx
# Autoriser seulement ces IPs / Allow only these IPs
allow 203.0.113.0/24;    # Votre réseau / Your network
allow 198.51.100.50;     # Votre IP / Your IP
deny all;                # Bloquer le reste / Block others
```

## 🔍 Vérification / Verification

### Tester la Configuration / Test Configuration

```bash
# Tester la syntaxe Nginx
sudo nginx -t

# Vérifier que Nginx écoute sur les bons ports
sudo ss -tulpn | grep nginx

# Vérifier le statut du service
sudo systemctl status nginx
```

### Vérifier SSL / Check SSL

```bash
# Voir les certificats installés
sudo certbot certificates

# Tester le renouvellement
sudo certbot renew --dry-run

# Vérifier SSL en ligne
# Ouvrir dans un navigateur:
# https://www.ssllabs.com/ssltest/analyze.html?d=votre-domaine.com
```

### Tester depuis l'Extérieur / Test from Outside

```bash
# Test HTTP redirect
curl -I http://votre-domaine.com

# Test HTTPS
curl -I https://votre-domaine.com

# Test complet
curl -vk https://votre-domaine.com
```

## 📊 Logs / Logging

### Voir les Logs / View Logs

```bash
# Logs d'accès / Access logs
sudo tail -f /var/log/nginx/netbox_access.log

# Logs d'erreur / Error logs
sudo tail -f /var/log/nginx/netbox_error.log

# Tous les logs Nginx / All Nginx logs
sudo tail -f /var/log/nginx/*.log
```

## 🛠️ Dépannage / Troubleshooting

### Problème: 502 Bad Gateway

```bash
# Vérifier que NetBox est en cours d'exécution
docker compose ps

# Vérifier les logs NetBox
cd ~/netbox-docker && docker compose logs -f netbox

# Vérifier la connexion proxy
curl http://localhost:8000
```

### Problème: Certificate Errors

```bash
# Forcer le renouvellement du certificat
sudo certbot renew --force-renewal

# Vérifier les permissions
sudo ls -l /etc/letsencrypt/live/
```

### Problème: Cannot Access from Internet

```bash
# Vérifier le pare-feu
sudo ufw status

# Vérifier les ports ouverts
sudo ss -tulpn | grep -E ':(80|443)'

# Vérifier le DNS
nslookup votre-domaine.com
```

## 🔒 Sécurité / Security

### Headers de Sécurité Inclus / Included Security Headers

Notre configuration HTTPS inclut:
- `Strict-Transport-Security` (HSTS)
- `X-Frame-Options`
- `X-Content-Type-Options`
- `X-XSS-Protection`
- `Referrer-Policy`
- `Content-Security-Policy`

### Recommandations / Recommendations

1. ✅ Toujours utiliser HTTPS en production
2. ✅ Activer Fail2Ban pour bloquer les attaques
3. ✅ Surveiller les logs régulièrement
4. ✅ Mettre à jour Nginx régulièrement
5. ✅ Tester la configuration SSL sur SSLLabs
6. ✅ Configurer des sauvegardes automatiques
7. ✅ Limiter l'accès par IP si possible

## 📚 Ressources / Resources

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Labs Test](https://www.ssllabs.com/ssltest/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

## ⚡ Performance Tips

Pour améliorer les performances:

1. **Activer le cache navigateur** (déjà inclus dans netbox-https.conf)
2. **Activer la compression Gzip** (déjà inclus)
3. **Utiliser HTTP/2** (déjà activé avec `http2`)
4. **Augmenter les workers Nginx** si beaucoup de trafic:

```nginx
# Dans /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 2048;
```

---

Pour plus d'informations, voir [NETBOX_INTERNET_ACCESS.md](../NETBOX_INTERNET_ACCESS.md)
