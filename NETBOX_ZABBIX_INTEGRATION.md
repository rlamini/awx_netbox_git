# Guide d'Intégration Zabbix ↔ NetBox / Zabbix-NetBox Integration Guide

## 📋 Aperçu / Overview

L'intégration de Zabbix avec NetBox combine le meilleur des deux mondes:
- **NetBox** = Source de vérité pour votre infrastructure (IPAM, DCIM, inventaire)
- **Zabbix** = Monitoring en temps réel de cette infrastructure

Combining Zabbix with NetBox provides:
- NetBox as the source of truth for infrastructure (IPAM, DCIM, inventory)
- Zabbix for real-time monitoring of that infrastructure

## 🎯 Avantages de l'Intégration / Integration Benefits

### 1. Synchronisation Automatique / Automatic Synchronization
- ✅ Hôtes NetBox → Hôtes Zabbix automatiquement
- ✅ Mises à jour en temps réel
- ✅ Pas de double saisie

### 2. Source de Vérité Unique / Single Source of Truth
- ✅ NetBox contient toute l'info infrastructure
- ✅ Zabbix surveille basé sur ces données
- ✅ Cohérence garantie

### 3. Automatisation Complète / Full Automation
- ✅ Nouveau serveur dans NetBox → Monitoring automatique
- ✅ Serveur retiré → Monitoring arrêté
- ✅ Changement d'IP → Mise à jour automatique

### 4. Métadonnées Enrichies / Enriched Metadata
- ✅ Tags NetBox → Groupes Zabbix
- ✅ Custom fields → Variables Zabbix
- ✅ Sites, racks, rôles → Organisation Zabbix

## 🔧 Méthodes d'Intégration / Integration Methods

### Méthode 1: Scripts Python (Recommandé)
Utilisation des API NetBox et Zabbix pour synchroniser

### Méthode 2: Zabbix Low-Level Discovery
Découverte dynamique via l'API NetBox

### Méthode 3: AWX/Ansible
Orchestration avec Ansible playbooks

### Méthode 4: Webhooks NetBox
Synchronisation en temps réel via webhooks

## 📦 Prérequis / Prerequisites

1. **NetBox** installé et accessible
2. **Zabbix** installé et accessible
3. **Token API NetBox** avec permissions lecture
4. **Credentials Zabbix** avec permissions API
5. **Python 3.8+** pour les scripts
6. **Bibliothèques Python**:
   ```bash
   pip install pynetbox pyzabbix requests
   ```

## 🔑 Étape 1 : Créer un Token API NetBox / Step 1: Create NetBox API Token

### Dans NetBox:

1. Connectez-vous à NetBox
2. Allez dans **votre profil** (coin supérieur droit)
3. Cliquez sur **API Tokens**
4. Cliquez sur **Add a token**
5. Configurez:
   - **Allowed IPs**: Laisser vide pour autoriser toutes les IPs
   - **Write enabled**: Non (lecture seule suffit)
6. Cliquez sur **Create**
7. **COPIEZ LE TOKEN** (vous ne le reverrez plus!)

**Exemple de token:**
```
f4d8e6c2a1b3e5f7g9h1i3j5k7l9m1n3o5p7q9r1s3t5
```

### Tester le Token:

```bash
# Remplacez par votre URL et token
NETBOX_URL="http://localhost:8000"
NETBOX_TOKEN="votre_token_ici"

curl -H "Authorization: Token ${NETBOX_TOKEN}" \
     -H "Content-Type: application/json" \
     "${NETBOX_URL}/api/dcim/devices/"
```

## 🔑 Étape 2 : Configurer l'Accès API Zabbix / Step 2: Configure Zabbix API Access

### Dans Zabbix:

1. Connectez-vous à Zabbix
2. Allez dans **Administration** → **Users**
3. Créez un utilisateur **zabbix-api** (ou utilisez admin)
4. Notez le **username** et **password**

### Tester l'API Zabbix:

```bash
# Test de connexion API Zabbix
ZABBIX_URL="http://localhost:8080/api_jsonrpc.php"
ZABBIX_USER="Admin"
ZABBIX_PASS="zabbix"

curl -X POST "${ZABBIX_URL}" \
     -H "Content-Type: application/json-rpc" \
     -d '{
       "jsonrpc": "2.0",
       "method": "user.login",
       "params": {
         "user": "'${ZABBIX_USER}'",
         "password": "'${ZABBIX_PASS}'"
       },
       "id": 1
     }'
```

## 📝 Étape 3 : Script de Synchronisation Python / Step 3: Python Sync Script

### Créer le Script de Synchronisation:

Créez un fichier `netbox_to_zabbix_sync.py`:

```python
#!/usr/bin/env python3
"""
Script de synchronisation NetBox → Zabbix
Synchronise les devices NetBox vers les hôtes Zabbix
"""

import sys
from pynetbox import api as netbox_api
from pyzabbix import ZabbixAPI
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION - Modifier ces valeurs
# ============================================

# NetBox Configuration
NETBOX_URL = "http://localhost:8000"
NETBOX_TOKEN = "votre_token_netbox_ici"

# Zabbix Configuration
ZABBIX_URL = "http://localhost:8080"
ZABBIX_USER = "Admin"
ZABBIX_PASSWORD = "zabbix"

# Groupe Zabbix par défaut
DEFAULT_HOST_GROUP = "NetBox Devices"

# Template Zabbix par défaut
DEFAULT_TEMPLATE = "Linux by Zabbix agent"

# ============================================


class NetBoxZabbixSync:
    """Classe pour synchroniser NetBox avec Zabbix"""

    def __init__(self):
        """Initialisation des connexions API"""
        logger.info("Connexion à NetBox...")
        self.netbox = netbox_api(NETBOX_URL, token=NETBOX_TOKEN)

        logger.info("Connexion à Zabbix...")
        self.zabbix = ZabbixAPI(ZABBIX_URL)
        self.zabbix.login(ZABBIX_USER, ZABBIX_PASSWORD)

        logger.info("✅ Connexions établies")

    def get_or_create_host_group(self, group_name):
        """Obtient ou crée un groupe d'hôtes Zabbix"""
        try:
            # Chercher le groupe existant
            groups = self.zabbix.hostgroup.get(
                filter={"name": group_name}
            )

            if groups:
                return groups[0]['groupid']

            # Créer le groupe s'il n'existe pas
            logger.info(f"Création du groupe: {group_name}")
            result = self.zabbix.hostgroup.create(name=group_name)
            return result['groupids'][0]

        except Exception as e:
            logger.error(f"Erreur lors de la création du groupe {group_name}: {e}")
            return None

    def get_template_id(self, template_name):
        """Obtient l'ID d'un template Zabbix"""
        try:
            templates = self.zabbix.template.get(
                filter={"host": template_name}
            )

            if templates:
                return templates[0]['templateid']

            logger.warning(f"Template {template_name} non trouvé")
            return None

        except Exception as e:
            logger.error(f"Erreur lors de la recherche du template: {e}")
            return None

    def sync_devices(self):
        """Synchronise les devices NetBox vers Zabbix"""
        logger.info("🔄 Début de la synchronisation...")

        # Obtenir tous les devices actifs de NetBox
        devices = self.netbox.dcim.devices.filter(status='active')

        logger.info(f"📦 {len(devices)} devices trouvés dans NetBox")

        synced_count = 0
        skipped_count = 0
        error_count = 0

        for device in devices:
            try:
                # Extraire les informations
                device_name = device.name

                # Obtenir l'adresse IP primaire
                if device.primary_ip4:
                    device_ip = str(device.primary_ip4).split('/')[0]
                elif device.primary_ip6:
                    device_ip = str(device.primary_ip6).split('/')[0]
                else:
                    logger.warning(f"⚠️  {device_name}: Pas d'IP - ignoré")
                    skipped_count += 1
                    continue

                # Déterminer le groupe Zabbix basé sur le site NetBox
                if device.site:
                    group_name = f"NetBox - {device.site.name}"
                else:
                    group_name = DEFAULT_HOST_GROUP

                group_id = self.get_or_create_host_group(group_name)

                if not group_id:
                    logger.error(f"❌ {device_name}: Impossible de créer le groupe")
                    error_count += 1
                    continue

                # Obtenir le template ID
                template_id = self.get_template_id(DEFAULT_TEMPLATE)

                # Vérifier si l'hôte existe déjà dans Zabbix
                existing_hosts = self.zabbix.host.get(
                    filter={"host": device_name}
                )

                if existing_hosts:
                    # Mettre à jour l'hôte existant
                    host_id = existing_hosts[0]['hostid']

                    self.zabbix.host.update(
                        hostid=host_id,
                        host=device_name,
                        interfaces=[{
                            "type": 1,  # Agent
                            "main": 1,
                            "useip": 1,
                            "ip": device_ip,
                            "dns": "",
                            "port": "10050"
                        }]
                    )

                    logger.info(f"🔄 {device_name} ({device_ip}) - Mis à jour")

                else:
                    # Créer un nouvel hôte
                    host_params = {
                        "host": device_name,
                        "interfaces": [{
                            "type": 1,  # Agent
                            "main": 1,
                            "useip": 1,
                            "ip": device_ip,
                            "dns": "",
                            "port": "10050"
                        }],
                        "groups": [{"groupid": group_id}]
                    }

                    # Ajouter le template si disponible
                    if template_id:
                        host_params["templates"] = [{"templateid": template_id}]

                    self.zabbix.host.create(**host_params)

                    logger.info(f"✅ {device_name} ({device_ip}) - Créé")

                synced_count += 1

            except Exception as e:
                logger.error(f"❌ Erreur pour {device.name}: {e}")
                error_count += 1

        # Résumé
        logger.info("=" * 60)
        logger.info("📊 Résumé de la synchronisation:")
        logger.info(f"   ✅ Synchronisés: {synced_count}")
        logger.info(f"   ⚠️  Ignorés: {skipped_count}")
        logger.info(f"   ❌ Erreurs: {error_count}")
        logger.info("=" * 60)

    def sync_with_tags(self):
        """Synchronisation avancée avec support des tags NetBox"""
        logger.info("🔄 Synchronisation avec tags...")

        devices = self.netbox.dcim.devices.filter(status='active')

        for device in devices:
            try:
                device_name = device.name

                # Obtenir l'IP
                if not device.primary_ip4 and not device.primary_ip6:
                    continue

                device_ip = str(device.primary_ip4 or device.primary_ip6).split('/')[0]

                # Créer des groupes basés sur les tags
                group_ids = []

                if device.tags:
                    for tag in device.tags:
                        group_name = f"NetBox Tag - {tag.name}"
                        group_id = self.get_or_create_host_group(group_name)
                        if group_id:
                            group_ids.append({"groupid": group_id})

                # Ajouter le groupe par défaut
                default_group_id = self.get_or_create_host_group(DEFAULT_HOST_GROUP)
                if default_group_id:
                    group_ids.append({"groupid": default_group_id})

                # Vérifier si existe
                existing_hosts = self.zabbix.host.get(filter={"host": device_name})

                if existing_hosts:
                    # Mise à jour
                    host_id = existing_hosts[0]['hostid']
                    self.zabbix.host.update(
                        hostid=host_id,
                        groups=group_ids
                    )
                    logger.info(f"🔄 {device_name} - Tags mis à jour")
                else:
                    # Création
                    self.zabbix.host.create(
                        host=device_name,
                        interfaces=[{
                            "type": 1,
                            "main": 1,
                            "useip": 1,
                            "ip": device_ip,
                            "dns": "",
                            "port": "10050"
                        }],
                        groups=group_ids
                    )
                    logger.info(f"✅ {device_name} - Créé avec tags")

            except Exception as e:
                logger.error(f"❌ Erreur pour {device.name}: {e}")


def main():
    """Fonction principale"""
    try:
        # Créer l'instance de synchronisation
        sync = NetBoxZabbixSync()

        # Lancer la synchronisation
        sync.sync_devices()

        # Optionnel: Synchronisation avec tags
        # sync.sync_with_tags()

        logger.info("✅ Synchronisation terminée!")

    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Installer les Dépendances:

```bash
# Créer un environnement virtuel (recommandé)
python3 -m venv netbox-zabbix-env
source netbox-zabbix-env/bin/activate

# Installer les bibliothèques
pip install pynetbox pyzabbix requests
```

### Configurer et Exécuter:

```bash
# Modifier le script avec vos informations
nano netbox_to_zabbix_sync.py

# Modifier ces variables:
# - NETBOX_URL
# - NETBOX_TOKEN
# - ZABBIX_URL
# - ZABBIX_USER
# - ZABBIX_PASSWORD

# Rendre le script exécutable
chmod +x netbox_to_zabbix_sync.py

# Exécuter la synchronisation
./netbox_to_zabbix_sync.py
```

## ⏰ Étape 4 : Automatisation avec Cron / Step 4: Automation with Cron

### Synchronisation Périodique:

```bash
# Éditer le crontab
crontab -e

# Ajouter une ligne pour synchroniser toutes les heures
0 * * * * /usr/bin/python3 /path/to/netbox_to_zabbix_sync.py >> /var/log/netbox-zabbix-sync.log 2>&1

# Ou toutes les 15 minutes
*/15 * * * * /usr/bin/python3 /path/to/netbox_to_zabbix_sync.py >> /var/log/netbox-zabbix-sync.log 2>&1
```

### Script de Surveillance des Logs:

```bash
# Voir les logs en temps réel
tail -f /var/log/netbox-zabbix-sync.log

# Voir les dernières synchronisations
tail -n 50 /var/log/netbox-zabbix-sync.log
```

## 🔔 Étape 5 : Webhooks NetBox (Temps Réel) / Step 5: NetBox Webhooks (Real-time)

### Configuration des Webhooks NetBox:

1. Dans NetBox, allez dans **Admin** → **Webhooks**
2. Cliquez sur **Add**
3. Configurez:
   - **Name**: `Zabbix Sync on Device Change`
   - **Object type**: `dcim > device`
   - **Enabled**: ✅
   - **Events**: Cochez `Creations`, `Updates`, `Deletions`
   - **HTTP method**: `POST`
   - **URL**: `http://votre-serveur:5000/webhook/netbox`
   - **HTTP content type**: `application/json`

### Script Webhook Receiver (Flask):

Créez `webhook_receiver.py`:

```python
#!/usr/bin/env python3
"""
Webhook receiver pour synchronisation temps réel NetBox → Zabbix
"""

from flask import Flask, request, jsonify
from pyzabbix import ZabbixAPI
import logging

app = Flask(__name__)

# Configuration
ZABBIX_URL = "http://localhost:8080"
ZABBIX_USER = "Admin"
ZABBIX_PASSWORD = "zabbix"

# Connexion Zabbix
zabbix = ZabbixAPI(ZABBIX_URL)
zabbix.login(ZABBIX_USER, ZABBIX_PASSWORD)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/webhook/netbox', methods=['POST'])
def netbox_webhook():
    """Endpoint pour recevoir les webhooks NetBox"""
    try:
        data = request.get_json()

        event = data.get('event')
        model = data.get('model')
        device_data = data.get('data')

        logger.info(f"Webhook reçu: {event} pour {model}")

        if model == 'device':
            if event == 'created' or event == 'updated':
                # Synchroniser le device
                sync_device_to_zabbix(device_data)

            elif event == 'deleted':
                # Supprimer de Zabbix
                delete_device_from_zabbix(device_data)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Erreur webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def sync_device_to_zabbix(device):
    """Synchronise un device vers Zabbix"""
    # Logique de synchronisation similaire au script principal
    pass


def delete_device_from_zabbix(device):
    """Supprime un device de Zabbix"""
    try:
        device_name = device.get('name')

        hosts = zabbix.host.get(filter={"host": device_name})

        if hosts:
            host_id = hosts[0]['hostid']
            zabbix.host.delete(host_id)
            logger.info(f"✅ Device {device_name} supprimé de Zabbix")

    except Exception as e:
        logger.error(f"Erreur suppression: {e}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 📊 Étape 6 : Templates Zabbix pour NetBox / Step 6: Zabbix Templates for NetBox

### Créer un Template Spécifique NetBox:

1. Dans Zabbix, allez dans **Configuration** → **Templates**
2. Cliquez sur **Create template**
3. Configurez:
   - **Template name**: `NetBox Device`
   - **Groups**: `Templates/Modules`
4. Ajoutez des items:
   - Utilisation CPU
   - Utilisation mémoire
   - Espace disque
   - Trafic réseau
5. Créez des triggers pour les alertes
6. Créez des graphs

### Appliquer le Template aux Hôtes NetBox:

Modifiez le script de synchronisation pour utiliser ce template:

```python
# Dans la fonction sync_devices():
DEFAULT_TEMPLATE = "NetBox Device"  # Votre nouveau template
```

## 🔗 Étape 7 : Intégration avec AWX (Optionnel) / Step 7: AWX Integration

### Créer un Playbook Ansible:

`netbox_zabbix_sync.yml`:

```yaml
---
- name: Synchronisation NetBox vers Zabbix
  hosts: localhost
  gather_facts: no
  vars:
    netbox_url: "http://localhost:8000"
    netbox_token: "{{ lookup('env', 'NETBOX_TOKEN') }}"
    zabbix_url: "http://localhost:8080"
    zabbix_user: "Admin"
    zabbix_password: "{{ lookup('env', 'ZABBIX_PASSWORD') }}"

  tasks:
    - name: Obtenir les devices NetBox
      uri:
        url: "{{ netbox_url }}/api/dcim/devices/"
        headers:
          Authorization: "Token {{ netbox_token }}"
        return_content: yes
      register: netbox_devices

    - name: Afficher le nombre de devices
      debug:
        msg: "{{ netbox_devices.json.count }} devices trouvés"

    - name: Exécuter le script de synchronisation
      command: /path/to/netbox_to_zabbix_sync.py
      register: sync_result

    - name: Afficher le résultat
      debug:
        var: sync_result.stdout
```

### Configurer dans AWX:

1. Créez un **Project** pointant vers votre repo Git
2. Créez un **Job Template** avec le playbook
3. Planifiez l'exécution (toutes les heures par exemple)
4. Activez les notifications

## 📈 Cas d'Usage Avancés / Advanced Use Cases

### 1. Synchronisation Bidirectionnelle

Mettre à jour NetBox avec les données de monitoring Zabbix:

```python
def sync_zabbix_to_netbox(self):
    """Synchronise les données Zabbix vers NetBox"""
    # Obtenir les problèmes Zabbix
    problems = self.zabbix.problem.get()

    for problem in problems:
        # Créer un journal dans NetBox
        # Ou mettre à jour le statut du device
        pass
```

### 2. Auto-Découverte Réseau

Utiliser Zabbix pour découvrir et ajouter à NetBox:

```python
def discover_and_add_to_netbox(self):
    """Découvre avec Zabbix et ajoute à NetBox"""
    discovered = self.zabbix.drule.get(selectDHosts='extend')

    for host in discovered:
        # Vérifier si existe dans NetBox
        # Sinon, créer le device
        pass
```

### 3. Synchronisation des Métriques

Envoyer les métriques Zabbix vers NetBox custom fields:

```python
def update_netbox_metrics(self):
    """Met à jour les custom fields NetBox avec les métriques Zabbix"""
    for device in self.netbox.dcim.devices.all():
        # Obtenir les dernières métriques de Zabbix
        metrics = self.get_zabbix_metrics(device.name)

        # Mettre à jour les custom fields
        device.custom_fields['cpu_usage'] = metrics['cpu']
        device.custom_fields['memory_usage'] = metrics['memory']
        device.save()
```

## 🛠️ Dépannage / Troubleshooting

### Problème: "Connection refused" à NetBox

```bash
# Vérifier que NetBox est accessible
curl http://localhost:8000/api/

# Vérifier le token
curl -H "Authorization: Token VOTRE_TOKEN" http://localhost:8000/api/dcim/devices/
```

### Problème: "Authentication failed" à Zabbix

```bash
# Vérifier les credentials Zabbix
curl -X POST http://localhost:8080/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d '{"jsonrpc":"2.0","method":"user.login","params":{"user":"Admin","password":"zabbix"},"id":1}'
```

### Problème: Script ne trouve pas les modules Python

```bash
# Installer dans l'environnement virtuel
source netbox-zabbix-env/bin/activate
pip install pynetbox pyzabbix requests

# Ou globalement (non recommandé)
sudo pip3 install pynetbox pyzabbix requests
```

### Problème: Hosts créés mais pas de monitoring

```bash
# Vérifier que l'agent Zabbix est installé sur les hôtes
sudo systemctl status zabbix-agent

# Vérifier que le template est appliqué
# Dans Zabbix UI: Configuration → Hosts → [Votre host] → Templates
```

## 📚 Ressources / Resources

- [NetBox API Documentation](https://docs.netbox.dev/en/stable/integrations/rest-api/)
- [Zabbix API Documentation](https://www.zabbix.com/documentation/current/en/manual/api)
- [pynetbox Documentation](https://pynetbox.readthedocs.io/)
- [pyzabbix Documentation](https://github.com/lukecyca/pyzabbix)

## 💡 Bonnes Pratiques / Best Practices

1. ✅ **Synchronisation régulière** - Toutes les 15-30 minutes
2. ✅ **Logs détaillés** - Pour le débogage
3. ✅ **Gestion des erreurs** - Ne pas arrêter sur une erreur
4. ✅ **Tags cohérents** - Utiliser les mêmes tags NetBox/Zabbix
5. ✅ **Templates standardisés** - Un template par type de device
6. ✅ **Webhooks** - Pour synchronisation temps réel
7. ✅ **Backup** - Sauvegarder avant synchronisation massive
8. ✅ **Tests** - Tester sur environnement de dev d'abord

## 🎯 Architecture Complète

```
┌─────────────────────────────────────────────────────┐
│                    NetBox                           │
│  - Devices, IPs, Sites, Racks, etc.               │
│  - Source de vérité infrastructure                │
└──────────────────┬──────────────────────────────────┘
                   │ API
                   │
         ┌─────────▼──────────┐
         │  Script Python     │
         │  - Synchronisation │
         │  - Cron/AWX       │
         └─────────┬──────────┘
                   │ API
                   │
┌──────────────────▼──────────────────────────────────┐
│                   Zabbix                            │
│  - Hosts automatiquement créés                     │
│  - Groupes basés sur sites NetBox                 │
│  - Tags synchro Nisés                              │
│  - Monitoring temps réel                           │
└─────────────────────────────────────────────────────┘
```

---

**Intégration NetBox + Zabbix** : La combinaison parfaite! 🎉

**NetBox + Zabbix Integration**: The perfect combination! 🎉
