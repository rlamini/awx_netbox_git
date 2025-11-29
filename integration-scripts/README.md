# NetBox-Zabbix Integration Scripts

Scripts d'intégration pour synchroniser NetBox et Zabbix.
Integration scripts to synchronize NetBox and Zabbix.

## 📁 Fichiers / Files

- `netbox_to_zabbix_sync.py` - Script principal de synchronisation / Main sync script
- `requirements.txt` - Dépendances Python / Python dependencies
- `.env.example` - Exemple de configuration / Example configuration

## 🚀 Installation Rapide / Quick Setup

### 1. Installer les Dépendances / Install Dependencies

```bash
# Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configurer les Variables d'Environnement / Configure Environment

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer avec vos valeurs
nano .env
```

**Modifier ces variables / Update these variables:**
- `NETBOX_URL` - URL de votre NetBox
- `NETBOX_TOKEN` - Token API NetBox
- `ZABBIX_URL` - URL de votre Zabbix
- `ZABBIX_USER` - Utilisateur Zabbix
- `ZABBIX_PASSWORD` - Mot de passe Zabbix

### 3. Obtenir un Token NetBox / Get NetBox API Token

1. Connectez-vous à NetBox
2. Allez dans votre **profil utilisateur**
3. Cliquez sur **API Tokens**
4. Créez un nouveau token
5. Copiez le token dans `.env`

### 4. Exécuter la Synchronisation / Run Synchronization

```bash
# Rendre le script exécutable
chmod +x netbox_to_zabbix_sync.py

# Exécuter
./netbox_to_zabbix_sync.py

# Ou avec Python
python3 netbox_to_zabbix_sync.py
```

## ⏰ Automatisation / Automation

### Avec Cron (Linux)

```bash
# Éditer crontab
crontab -e

# Synchroniser toutes les heures
0 * * * * /path/to/venv/bin/python3 /path/to/netbox_to_zabbix_sync.py

# Ou toutes les 15 minutes
*/15 * * * * /path/to/venv/bin/python3 /path/to/netbox_to_zabbix_sync.py
```

### Avec systemd (Service + Timer)

Créez `/etc/systemd/system/netbox-zabbix-sync.service`:

```ini
[Unit]
Description=NetBox to Zabbix Synchronization
After=network.target

[Service]
Type=oneshot
User=zabbix
Group=zabbix
WorkingDirectory=/opt/integration-scripts
EnvironmentFile=/opt/integration-scripts/.env
ExecStart=/opt/integration-scripts/venv/bin/python3 /opt/integration-scripts/netbox_to_zabbix_sync.py

[Install]
WantedBy=multi-user.target
```

Créez `/etc/systemd/system/netbox-zabbix-sync.timer`:

```ini
[Unit]
Description=NetBox to Zabbix Sync Timer
Requires=netbox-zabbix-sync.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min

[Install]
WantedBy=timers.target
```

Activez:

```bash
sudo systemctl daemon-reload
sudo systemctl enable netbox-zabbix-sync.timer
sudo systemctl start netbox-zabbix-sync.timer

# Vérifier le statut
sudo systemctl status netbox-zabbix-sync.timer
```

## 📊 Utilisation / Usage

### Synchronisation Simple / Basic Sync

```bash
python3 netbox_to_zabbix_sync.py
```

### Avec Variables d'Environnement / With Environment Variables

```bash
NETBOX_URL=http://netbox.example.com \
NETBOX_TOKEN=abc123 \
ZABBIX_URL=http://zabbix.example.com \
ZABBIX_USER=Admin \
ZABBIX_PASSWORD=zabbix \
python3 netbox_to_zabbix_sync.py
```

### Voir les Logs / View Logs

```bash
# Logs en temps réel
tail -f /var/log/netbox-zabbix-sync.log

# Dernières synchronisations
tail -n 100 /var/log/netbox-zabbix-sync.log
```

## 🔧 Personnalisation / Customization

### Modifier le Template Zabbix / Change Zabbix Template

Dans `netbox_to_zabbix_sync.py`, modifier:

```python
DEFAULT_TEMPLATE = "Linux by Zabbix agent"  # Votre template
```

### Filtrer par Site NetBox / Filter by NetBox Site

Dans le script, utiliser:

```python
sync.sync_devices(filter_site='DC1')
```

### Synchroniser avec Tags / Sync with Tags

Dans le script, décommenter:

```python
sync.sync_with_tags()
```

## 🛠️ Dépannage / Troubleshooting

### Erreur "Module not found"

```bash
# Vérifier que vous êtes dans l'environnement virtuel
source venv/bin/activate

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur "Connection refused"

```bash
# Vérifier que NetBox est accessible
curl http://localhost:8000/api/

# Vérifier que Zabbix est accessible
curl http://localhost:8080/
```

### Erreur "Authentication failed"

```bash
# Vérifier le token NetBox
curl -H "Authorization: Token VOTRE_TOKEN" \
     http://localhost:8000/api/dcim/devices/

# Vérifier les credentials Zabbix
curl -X POST http://localhost:8080/api_jsonrpc.php \
     -H "Content-Type: application/json-rpc" \
     -d '{"jsonrpc":"2.0","method":"user.login","params":{"user":"Admin","password":"zabbix"},"id":1}'
```

### Hosts créés mais pas de monitoring

1. Vérifier que l'agent Zabbix est installé sur les hôtes:
   ```bash
   sudo systemctl status zabbix-agent
   ```

2. Vérifier que le template est appliqué dans Zabbix UI

3. Vérifier la connectivité réseau entre Zabbix et les hôtes

## 📚 Documentation Complète / Full Documentation

Voir [NETBOX_ZABBIX_INTEGRATION.md](../NETBOX_ZABBIX_INTEGRATION.md) pour:
- Guide complet d'intégration
- Webhooks temps réel
- Intégration AWX
- Cas d'usage avancés
- Templates Zabbix
- Synchronisation bidirectionnelle

## 💡 Exemples / Examples

### Exemple 1: Synchronisation Quotidienne

```bash
# Cron: Tous les jours à 2h du matin
0 2 * * * /path/to/venv/bin/python3 /path/to/netbox_to_zabbix_sync.py
```

### Exemple 2: Synchronisation par Site

Créez `sync_dc1.sh`:

```bash
#!/bin/bash
export FILTER_SITE="DC1"
/path/to/venv/bin/python3 /path/to/netbox_to_zabbix_sync.py
```

### Exemple 3: Notification par Email

Créez `sync_with_email.sh`:

```bash
#!/bin/bash
LOG_FILE="/tmp/sync_$(date +%Y%m%d_%H%M%S).log"

python3 netbox_to_zabbix_sync.py > "$LOG_FILE" 2>&1

# Envoyer email si erreurs
if grep -q "ERROR" "$LOG_FILE"; then
    mail -s "NetBox-Zabbix Sync Failed" admin@example.com < "$LOG_FILE"
fi
```

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésitez pas à:
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## 📝 License

MIT License - Voir le fichier LICENSE pour plus de détails.
