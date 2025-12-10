# Guide d'Intégration NetBox avec GitHub / NetBox-GitHub Integration Guide

## 📋 Vue d'ensemble / Overview

Ce guide explique comment connecter NetBox avec GitHub pour utiliser les **Data Sources** et récupérer automatiquement les **Configuration Contexts** depuis un repository GitHub.

This guide explains how to connect NetBox with GitHub to use **Data Sources** and automatically retrieve **Configuration Contexts** from a GitHub repository.

## 🎯 Cas d'usage / Use Cases

- 📦 Stocker les configuration contexts dans Git (versionning, historique)
- 🔄 Synchronisation automatique NetBox ↔ GitHub
- 👥 Collaboration en équipe via Pull Requests
- 🔙 Rollback facile en cas d'erreur
- 📝 Review des changements avant application
- 🤖 Intégration CI/CD

Store configuration contexts in Git with versioning, automatic sync, team collaboration via PRs, easy rollbacks, change reviews, and CI/CD integration.

## 🔧 Prérequis / Prerequisites

- ✅ NetBox installé et fonctionnel (voir NETBOX_DOCKER_SETUP.md)
- ✅ Accès administrateur à NetBox
- ✅ Compte GitHub
- ✅ Git installé sur le serveur NetBox

## 📦 Étape 1 : Installer Git / Step 1: Install Git

```bash
# Sur le serveur NetBox
sudo apt update
sudo apt install git -y

# Vérifier l'installation
git --version

# Configuration globale (optionnel mais recommandé)
git config --global user.name "NetBox Server"
git config --global user.email "netbox@votredomaine.com"
```

## 🔑 Étape 2 : Créer un Token GitHub / Step 2: Create GitHub Token

### 2.1 Créer un Repository GitHub

```bash
# Option 1: Via l'interface web GitHub
# 1. Allez sur https://github.com
# 2. Cliquez sur "New repository"
# 3. Nom: netbox-config-contexts
# 4. Description: NetBox Configuration Contexts
# 5. Public ou Private (selon vos besoins)
# 6. Cochez "Add a README file"
# 7. Cliquez "Create repository"

# Option 2: Via GitHub CLI (si installé)
gh repo create netbox-config-contexts --public --description "NetBox Configuration Contexts"
```

### 2.2 Créer un Personal Access Token (PAT)

**Via l'interface web GitHub:**

1. Allez sur **GitHub** → **Settings** → **Developer settings**
2. Cliquez sur **Personal access tokens** → **Tokens (classic)**
3. Cliquez sur **Generate new token** → **Generate new token (classic)**
4. Nom du token: `netbox-data-source`
5. Expiration: Choisissez la durée (recommandé: 1 an)
6. Sélectionnez les permissions:
   - ✅ **repo** (Full control of private repositories)
   - ✅ **read:org** (si repo dans une organisation)
7. Cliquez sur **Generate token**
8. ⚠️ **IMPORTANT**: Copiez le token **immédiatement** (vous ne pourrez plus le voir)

```bash
# Sauvegarder le token dans un endroit sûr
echo "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" > ~/github-token.txt
chmod 600 ~/github-token.txt
```

## 📁 Étape 3 : Structure du Repository GitHub / Step 3: GitHub Repository Structure

### 3.1 Cloner le repository localement

```bash
# Cloner le repo
cd ~
git clone https://github.com/VOTRE_USERNAME/netbox-config-contexts.git
cd netbox-config-contexts

# Créer la structure des dossiers
mkdir -p config-contexts
mkdir -p export-templates
mkdir -p scripts

# Créer un fichier README
cat > README.md <<'EOF'
# NetBox Configuration Contexts

Ce repository contient les configuration contexts pour NetBox.

## Structure

```
config-contexts/          # Configuration contexts en JSON
├── global/              # Contexts globaux
├── sites/               # Contexts par site
├── device-roles/        # Contexts par rôle
├── device-types/        # Contexts par type
└── manufacturers/       # Contexts par fabricant

export-templates/        # Templates d'export
scripts/                 # Scripts Python
```

## Synchronisation

Les configuration contexts sont synchronisés automatiquement avec NetBox toutes les heures.
EOF

git add README.md
git commit -m "Initial commit: Add README"
git push origin main
```

### 3.2 Créer des Configuration Contexts d'exemple

```bash
# Context global pour tous les devices
mkdir -p config-contexts/global
cat > config-contexts/global/ntp-dns.json <<'EOF'
{
  "ntp_servers": [
    "0.pool.ntp.org",
    "1.pool.ntp.org",
    "2.pool.ntp.org"
  ],
  "dns_servers": [
    "8.8.8.8",
    "8.8.4.4",
    "1.1.1.1"
  ],
  "domain": "example.com"
}
EOF

# Context pour les routeurs
mkdir -p config-contexts/device-roles
cat > config-contexts/device-roles/router.json <<'EOF'
{
  "routing": {
    "ospf": {
      "area": 0,
      "network": "10.0.0.0/8"
    },
    "bgp": {
      "as_number": 65000
    }
  },
  "logging": {
    "syslog_servers": [
      "10.0.1.100",
      "10.0.1.101"
    ]
  }
}
EOF

# Context pour les switches
cat > config-contexts/device-roles/switch.json <<'EOF'
{
  "vlans": {
    "management": 10,
    "users": 20,
    "servers": 30,
    "guests": 40
  },
  "spanning_tree": {
    "mode": "rapid-pvst",
    "priority": 32768
  },
  "snmp": {
    "community": "public",
    "location": "datacenter"
  }
}
EOF

# Context pour un site spécifique
mkdir -p config-contexts/sites
cat > config-contexts/sites/paris-dc1.json <<'EOF'
{
  "site_info": {
    "location": "Paris Datacenter 1",
    "timezone": "Europe/Paris",
    "contact": "noc@example.com"
  },
  "network": {
    "gateway": "10.1.0.1",
    "subnet": "10.1.0.0/16",
    "vlan_range": "100-199"
  }
}
EOF

# Context pour les devices Cisco
mkdir -p config-contexts/manufacturers
cat > config-contexts/manufacturers/cisco.json <<'EOF'
{
  "vendor": {
    "name": "Cisco",
    "support_email": "tac@cisco.com"
  },
  "ssh": {
    "version": 2,
    "timeout": 30
  },
  "enable_password": "{{VAULT_ENABLE_PASSWORD}}"
}
EOF

# Créer un fichier .gitignore
cat > .gitignore <<'EOF'
# Secrets et credentials
*secret*
*password*
*credential*
*.key
*.pem

# Fichiers temporaires
*.tmp
*.bak
*~
.DS_Store

# Sauf les exemples
!example-*.json
EOF

# Committer et pousser
git add .
git commit -m "Add initial configuration contexts"
git push origin main
```

## 🔌 Étape 4 : Configurer NetBox Data Source / Step 4: Configure NetBox Data Source

### 4.1 Accéder à l'interface NetBox

```bash
# Ouvrir NetBox dans le navigateur
http://VOTRE_IP:8000

# Se connecter avec admin
```

### 4.2 Créer une Data Source

**Via l'interface Web:**

1. Allez dans **Operations** → **Data Sources** → **Add**

2. Remplissez les champs:
   - **Name**: `GitHub Config Contexts`
   - **Type**: `Git`
   - **Source URL**: `https://github.com/VOTRE_USERNAME/netbox-config-contexts.git`
   - **Branch**: `main`
   - **Enabled**: ✅ Coché
   - **Description**: `Configuration contexts from GitHub`

3. **Authentication:**
   - **Username**: Votre username GitHub
   - **Password**: Le token GitHub (ghp_xxxxx...)

4. **Parameters:**
   - Laissez vide pour l'instant

5. **Sync Schedule:**
   - **Interval**: `60` (synchronisation toutes les heures)

6. Cliquez sur **Create**

### 4.3 Créer des Data Files

Après avoir créé la Data Source, vous devez créer des **Data Files** pour spécifier quels fichiers synchroniser.

1. Dans la Data Source créée, cliquez sur **Data Files**

2. Cliquez sur **Add Data File**

3. Créez un Data File pour chaque type de context:

**Data File 1: Global NTP/DNS**
```
Path: config-contexts/global/ntp-dns.json
Auto-sync: ✅ Enabled
```

**Data File 2: Routeurs**
```
Path: config-contexts/device-roles/router.json
Auto-sync: ✅ Enabled
```

**Data File 3: Switches**
```
Path: config-contexts/device-roles/switch.json
Auto-sync: ✅ Enabled
```

**Data File 4: Site Paris**
```
Path: config-contexts/sites/paris-dc1.json
Auto-sync: ✅ Enabled
```

### 4.4 Créer les Configuration Contexts dans NetBox

Maintenant, créez les Configuration Contexts qui utiliseront les fichiers du repository:

1. Allez dans **Customization** → **Configuration Contexts** → **Add**

2. **Context Global NTP/DNS:**
   - **Name**: `Global NTP DNS`
   - **Weight**: `1000` (priorité basse)
   - **Is Active**: ✅
   - **Data Source**: `GitHub Config Contexts`
   - **Data File**: `config-contexts/global/ntp-dns.json`
   - **Auto Sync Enabled**: ✅
   - Ne sélectionnez aucun filtre (s'applique à tous les devices)

3. **Context Routeurs:**
   - **Name**: `Router Configuration`
   - **Weight**: `2000`
   - **Is Active**: ✅
   - **Data Source**: `GitHub Config Contexts`
   - **Data File**: `config-contexts/device-roles/router.json`
   - **Auto Sync Enabled**: ✅
   - **Device Roles**: Sélectionnez "Router"

4. **Context Switches:**
   - **Name**: `Switch Configuration`
   - **Weight**: `2000`
   - **Is Active**: ✅
   - **Data Source**: `GitHub Config Contexts`
   - **Data File**: `config-contexts/device-roles/switch.json`
   - **Auto Sync Enabled**: ✅
   - **Device Roles**: Sélectionnez "Switch"

5. **Context Site Paris:**
   - **Name**: `Paris DC1 Configuration`
   - **Weight**: `3000` (priorité haute)
   - **Is Active**: ✅
   - **Data Source**: `GitHub Config Contexts`
   - **Data File**: `config-contexts/sites/paris-dc1.json`
   - **Auto Sync Enabled**: ✅
   - **Sites**: Sélectionnez "Paris DC1"

## 🔄 Étape 5 : Synchronisation Manuelle / Step 5: Manual Sync

### 5.1 Première synchronisation

```bash
# Via l'interface NetBox:
# 1. Allez dans Operations → Data Sources
# 2. Cliquez sur "GitHub Config Contexts"
# 3. Cliquez sur "Sync" (icône de rotation)

# Via l'API NetBox:
curl -X POST \
  http://localhost:8000/api/core/data-sources/1/sync/ \
  -H "Authorization: Token VOTRE_TOKEN_NETBOX" \
  -H "Content-Type: application/json"
```

### 5.2 Vérifier la synchronisation

```bash
# Via l'interface:
# 1. Allez dans Operations → Data Sources
# 2. Cliquez sur "GitHub Config Contexts"
# 3. Regardez "Last Synced" et "Status"

# Via l'API:
curl -X GET \
  http://localhost:8000/api/core/data-sources/1/ \
  -H "Authorization: Token VOTRE_TOKEN_NETBOX"
```

### 5.3 Vérifier les Configuration Contexts

```bash
# Via l'interface:
# 1. Allez dans un Device
# 2. Onglet "Config Context"
# 3. Vous devriez voir les contexts appliqués

# Via l'API:
curl -X GET \
  "http://localhost:8000/api/dcim/devices/DEVICE_ID/?include=config_context" \
  -H "Authorization: Token VOTRE_TOKEN_NETBOX"
```

## 🤖 Étape 6 : Automatisation de la Synchronisation / Step 6: Automation

### 6.1 Synchronisation automatique via NetBox

NetBox synchronise automatiquement selon l'intervalle configuré (60 minutes par défaut).

### 6.2 Synchronisation manuelle via script

```bash
# Créer un script de synchronisation
cat > /opt/netbox-sync.sh <<'EOF'
#!/bin/bash

# Configuration
NETBOX_URL="http://localhost:8000"
NETBOX_TOKEN="VOTRE_TOKEN_NETBOX"
DATA_SOURCE_ID="1"

# Fonction de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Synchroniser la data source
log "Starting NetBox GitHub sync..."
RESPONSE=$(curl -s -X POST \
    "${NETBOX_URL}/api/core/data-sources/${DATA_SOURCE_ID}/sync/" \
    -H "Authorization: Token ${NETBOX_TOKEN}" \
    -H "Content-Type: application/json")

# Vérifier le résultat
if echo "$RESPONSE" | grep -q "id"; then
    log "✅ Sync successful"
else
    log "❌ Sync failed: $RESPONSE"
    exit 1
fi

# Attendre que la sync soit terminée
sleep 10

# Vérifier le statut
STATUS=$(curl -s -X GET \
    "${NETBOX_URL}/api/core/data-sources/${DATA_SOURCE_ID}/" \
    -H "Authorization: Token ${NETBOX_TOKEN}" \
    | jq -r '.last_synced')

log "Last synced: $STATUS"
EOF

# Rendre exécutable
chmod +x /opt/netbox-sync.sh

# Tester
/opt/netbox-sync.sh
```

### 6.3 Cron job pour synchronisation automatique

```bash
# Éditer le crontab
crontab -e

# Ajouter une ligne pour synchroniser toutes les heures
0 * * * * /opt/netbox-sync.sh >> /var/log/netbox-sync.log 2>&1

# Ou toutes les 30 minutes
*/30 * * * * /opt/netbox-sync.sh >> /var/log/netbox-sync.log 2>&1
```

## 🔧 Étape 7 : Workflow de Mise à Jour / Step 7: Update Workflow

### 7.1 Modifier un Configuration Context

```bash
# 1. Cloner ou pull le repo
cd ~/netbox-config-contexts
git pull origin main

# 2. Modifier un fichier
nano config-contexts/global/ntp-dns.json

# Exemple: Ajouter un serveur NTP
{
  "ntp_servers": [
    "0.pool.ntp.org",
    "1.pool.ntp.org",
    "2.pool.ntp.org",
    "time.google.com"
  ],
  ...
}

# 3. Committer et pousser
git add config-contexts/global/ntp-dns.json
git commit -m "Add Google NTP server"
git push origin main

# 4. Attendre la synchronisation automatique (ou déclencher manuellement)
```

### 7.2 Workflow avec Branches (Recommandé)

```bash
# 1. Créer une branche de développement
git checkout -b add-snmp-config

# 2. Faire les modifications
nano config-contexts/global/monitoring.json

# 3. Committer
git add .
git commit -m "Add SNMP monitoring configuration"

# 4. Pousser la branche
git push origin add-snmp-config

# 5. Créer une Pull Request sur GitHub
# - Aller sur GitHub
# - Cliquer sur "Compare & pull request"
# - Review des changements
# - Merge dans main

# 6. NetBox se synchronise automatiquement avec main
```

## 📊 Étape 8 : Exemples Avancés / Step 8: Advanced Examples

### 8.1 Config Context avec Variables

```json
{
  "snmp": {
    "version": "v3",
    "user": "netbox",
    "auth_protocol": "SHA",
    "priv_protocol": "AES",
    "engine_id": "{{ device.name }}"
  },
  "management": {
    "ip": "{{ device.primary_ip4.address }}",
    "hostname": "{{ device.name }}.{{ site.slug }}.example.com"
  }
}
```

### 8.2 Config Context Hiérarchique

```json
{
  "interfaces": {
    "default_mtu": 1500,
    "default_speed": "auto",
    "management": {
      "name": "Management1",
      "description": "Management Interface",
      "vlan": 10
    }
  },
  "services": {
    "ssh": {
      "enabled": true,
      "port": 22,
      "version": 2
    },
    "https": {
      "enabled": true,
      "port": 443
    }
  }
}
```

### 8.3 Config Context par Manufacturer

```bash
# Créer un context pour Huawei
cat > config-contexts/manufacturers/huawei.json <<'EOF'
{
  "vendor": {
    "name": "Huawei",
    "support_email": "support@huawei.com"
  },
  "cli": {
    "prompt": "<.*>",
    "enable_prompt": "<.*>",
    "commands": {
      "save_config": "save",
      "show_version": "display version",
      "show_interfaces": "display interface brief"
    }
  },
  "snmp": {
    "version": "v2c",
    "community": "public"
  }
}
EOF

git add config-contexts/manufacturers/huawei.json
git commit -m "Add Huawei manufacturer context"
git push origin main
```

## 🔍 Étape 9 : Validation et Tests / Step 9: Validation and Testing

### 9.1 Valider le JSON avant commit

```bash
# Installer jq pour validation JSON
sudo apt install jq -y

# Valider tous les fichiers JSON
find config-contexts -name "*.json" -type f -exec sh -c '
    echo "Validating: $1"
    if ! jq empty "$1" 2>/dev/null; then
        echo "❌ Invalid JSON: $1"
        exit 1
    fi
' _ {} \;

echo "✅ All JSON files are valid"
```

### 9.2 Pre-commit Hook pour validation

```bash
# Créer un pre-commit hook
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/bash

echo "Validating JSON files..."

# Trouver tous les fichiers JSON modifiés
JSON_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.json$')

if [ -n "$JSON_FILES" ]; then
    for file in $JSON_FILES; do
        if ! jq empty "$file" 2>/dev/null; then
            echo "❌ Invalid JSON: $file"
            exit 1
        fi
    done
    echo "✅ All JSON files are valid"
fi

exit 0
EOF

chmod +x .git/hooks/pre-commit
```

### 9.3 Tester un Config Context sur un Device

```bash
# Via l'API NetBox
curl -X GET \
  "http://localhost:8000/api/dcim/devices/?name=router01&include=config_context" \
  -H "Authorization: Token VOTRE_TOKEN_NETBOX" \
  | jq '.results[0].config_context'
```

## 🛠️ Dépannage / Troubleshooting

### Problème: Sync échoue avec erreur d'authentification

```bash
# Vérifier que le token GitHub est valide
curl -H "Authorization: token VOTRE_TOKEN_GITHUB" \
  https://api.github.com/user

# Vérifier les permissions du token
# Le token doit avoir la permission "repo"

# Re-générer un nouveau token si nécessaire
```

### Problème: Les fichiers ne sont pas synchronisés

```bash
# Vérifier que les Data Files sont configurés correctement
# Operations → Data Sources → GitHub Config Contexts → Data Files

# Vérifier que Auto Sync est activé sur les Config Contexts
# Customization → Configuration Contexts → Vérifier "Auto Sync Enabled"

# Forcer une synchronisation manuelle
# Operations → Data Sources → Sync
```

### Problème: Config Context ne s'applique pas au device

```bash
# Vérifier les filtres du Config Context
# Le context doit matcher le device (site, role, type, etc.)

# Vérifier le Weight (priorité)
# Un weight plus élevé = priorité plus haute

# Vérifier que "Is Active" est coché
```

### Problème: Erreur JSON Invalid

```bash
# Valider le JSON localement
jq empty config-contexts/global/ntp-dns.json

# Vérifier les virgules manquantes ou en trop
# Vérifier les guillemets
# Utiliser un éditeur avec validation JSON (VS Code, etc.)
```

## 📚 Exemples de Structure Complète

### Structure d'un Repository Complet

```
netbox-config-contexts/
├── README.md
├── .gitignore
├── config-contexts/
│   ├── global/
│   │   ├── ntp-dns.json
│   │   ├── syslog.json
│   │   └── snmp.json
│   ├── sites/
│   │   ├── paris-dc1.json
│   │   ├── london-dc1.json
│   │   └── nyc-dc1.json
│   ├── device-roles/
│   │   ├── router.json
│   │   ├── switch.json
│   │   ├── firewall.json
│   │   └── access-point.json
│   ├── device-types/
│   │   ├── cisco-catalyst-9300.json
│   │   ├── cisco-isr-4000.json
│   │   └── huawei-s5700.json
│   └── manufacturers/
│       ├── cisco.json
│       ├── huawei.json
│       └── juniper.json
├── export-templates/
│   ├── cisco-ios-config.j2
│   └── huawei-vrp-config.j2
└── scripts/
    ├── validate-json.sh
    └── sync-netbox.sh
```

## 🎯 Bonnes Pratiques / Best Practices

### 1. Organisation des fichiers

✅ **Bon:**
```
config-contexts/
├── global/           # Contexts pour tous les devices
├── sites/            # Contexts spécifiques par site
├── device-roles/     # Contexts par rôle
└── manufacturers/    # Contexts par fabricant
```

❌ **Mauvais:**
```
config-contexts/
├── context1.json
├── context2.json
└── my-config.json
```

### 2. Nommage des fichiers

✅ **Bon:** `ntp-dns.json`, `router-bgp.json`, `paris-dc1.json`

❌ **Mauvais:** `config.json`, `test.json`, `new-1.json`

### 3. Priorité (Weight)

```
1000 = Global (priorité basse)
2000 = Role/Type (priorité moyenne)
3000 = Site (priorité haute)
4000 = Device spécifique (priorité très haute)
```

### 4. Utilisation de branches

- `main` → Production (synchronisé avec NetBox)
- `staging` → Pré-production (tests)
- `feature/*` → Développement de nouvelles configs

### 5. Documentation

Toujours documenter vos config contexts:

```json
{
  "_comment": "Global NTP and DNS configuration for all devices",
  "_owner": "Network Team",
  "_last_updated": "2025-12-01",
  "ntp_servers": [
    "0.pool.ntp.org"
  ]
}
```

## 🚀 Prochaines Étapes / Next Steps

1. ✅ Créer d'autres config contexts pour vos devices
2. ✅ Intégrer avec des templates Jinja2 pour génération de configs
3. ✅ Automatiser avec CI/CD (GitHub Actions)
4. ✅ Créer des tests automatiques pour valider les JSON
5. ✅ Intégrer avec Ansible pour déploiement automatique

## 📖 Ressources / Resources

- [NetBox Documentation - Configuration Contexts](https://docs.netbox.dev/en/stable/models/extras/configcontext/)
- [NetBox Documentation - Data Sources](https://docs.netbox.dev/en/stable/models/core/datasource/)
- [GitHub Documentation - Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [JSON Schema Validation](https://json-schema.org/)

---

**NetBox + GitHub** : Configuration as Code! 🎉

**NetBox + GitHub**: Configuration as Code! 🎉
