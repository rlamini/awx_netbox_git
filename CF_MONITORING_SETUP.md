# Configuration du Custom Field cf_monitoring dans NetBox

## 📋 Guide de Configuration

Ce guide explique comment configurer le custom field `cf_monitoring` dans NetBox pour contrôler l'activation/désactivation du monitoring dans Zabbix.

This guide explains how to configure the `cf_monitoring` custom field in NetBox to control monitoring activation/deactivation in Zabbix.

## 🎯 Objectif / Goal

Contrôler depuis NetBox si un device doit être monitoré dans Zabbix:
- `cf_monitoring = yes` → Monitoring ACTIF dans Zabbix
- `cf_monitoring = no` → Monitoring DÉSACTIVÉ dans Zabbix

Control from NetBox whether a device should be monitored in Zabbix:
- `cf_monitoring = yes` → Monitoring ENABLED in Zabbix
- `cf_monitoring = no` → Monitoring DISABLED in Zabbix

## 📝 Étape 1 : Créer le Custom Field dans NetBox

### Via l'Interface Web NetBox:

1. **Connectez-vous** à NetBox en tant qu'administrateur

2. **Allez dans Customization**:
   - Cliquez sur votre profil (coin supérieur droit)
   - Sélectionnez **Admin** ou **Customization**
   - Ou accédez directement: `http://votre-netbox/admin/extras/customfield/`

3. **Créez le Custom Field**:
   - Cliquez sur **Add** ou **+ Add custom field**

4. **Configurez le champ**:

   | Paramètre | Valeur |
   |-----------|--------|
   | **Name** | `cf_monitoring` |
   | **Label** | `Monitoring` |
   | **Type** | `Selection` |
   | **Content types** | Cochez `dcim > device` |
   | **Required** | ❌ Non coché |
   | **Default** | `yes` (optionnel) |
   | **Weight** | `100` |
   | **Description** | `Enable or disable monitoring in Zabbix` |

5. **Configurez les Choices (Options)**:

   Dans le champ **Choices**, entrez:
   ```
   yes,no
   ```

   Ou utilisez le format YAML si disponible:
   ```yaml
   - value: yes
     weight: 100
   - value: no
     weight: 200
   ```

6. **Sauvegardez** le custom field

### Via l'API NetBox (Optionnel):

```bash
curl -X POST http://localhost:8000/api/extras/custom-fields/ \
  -H "Authorization: Token VOTRE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "cf_monitoring",
    "label": "Monitoring",
    "type": "select",
    "content_types": ["dcim.device"],
    "required": false,
    "default": "yes",
    "weight": 100,
    "description": "Enable or disable monitoring in Zabbix",
    "choices": ["yes", "no"]
  }'
```

## 🔧 Étape 2 : Utiliser le Custom Field

### Sur un Device Existant:

1. Allez dans **Devices** → **Devices**
2. Cliquez sur un device
3. Cliquez sur **Edit** (bouton modifier)
4. Scrollez jusqu'à la section **Custom Fields**
5. Vous verrez le champ **Monitoring** avec les options:
   - `yes` (monitoring actif)
   - `no` (monitoring désactivé)
6. Sélectionnez la valeur souhaitée
7. Cliquez sur **Save**

### Lors de la Création d'un Device:

1. **Devices** → **+ Add** (Ajouter un device)
2. Remplissez les champs obligatoires (Name, Device type, Site, etc.)
3. Dans la section **Custom Fields**, configurez **Monitoring**:
   - `yes` pour activer le monitoring
   - `no` pour désactiver le monitoring
4. Sauvegardez

### Via l'API:

```bash
# Activer le monitoring pour un device
curl -X PATCH http://localhost:8000/api/dcim/devices/1/ \
  -H "Authorization: Token VOTRE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_fields": {
      "cf_monitoring": "yes"
    }
  }'

# Désactiver le monitoring pour un device
curl -X PATCH http://localhost:8000/api/dcim/devices/1/ \
  -H "Authorization: Token VOTRE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_fields": {
      "cf_monitoring": "no"
    }
  }'
```

## 🔄 Étape 3 : Synchronisation avec Zabbix

### Automatique:

Le script de synchronisation (`netbox_to_zabbix_sync.py`) lit automatiquement le custom field et applique le statut dans Zabbix.

```bash
# Exécuter la synchronisation
cd integration-scripts
python3 netbox_to_zabbix_sync.py
```

### Résultat dans les Logs:

```
✅ server-001 (192.168.1.10) - Created | Status: ENABLED
✅ server-002 (192.168.1.11) - Created | Status: DISABLED
🔄 server-003 (192.168.1.12) - Updated | Status: ENABLED → DISABLED
```

## 📊 Comportement du Script

### Valeurs Supportées:

| Valeur NetBox | Résultat Zabbix | Description |
|---------------|-----------------|-------------|
| `yes` | Status: 0 (Enabled) | Monitoring actif |
| `no` | Status: 1 (Disabled) | Monitoring désactivé |
| `null` (vide) | Status: 0 (Enabled) | Par défaut: actif |
| Autre | Status: 0 (Enabled) | Par défaut: actif + warning |

### Logs de Changement de Statut:

Le script log les changements de statut:

```
🔄 server-001 (192.168.1.10) - Updated | Status: ENABLED → DISABLED
```

Cela vous permet de suivre quand un device a été désactivé ou réactivé.

## 💡 Cas d'Usage

### Cas 1: Désactiver Temporairement le Monitoring

**Scénario**: Maintenance planifiée sur un serveur

1. Dans NetBox, éditez le device
2. Changez `cf_monitoring` de `yes` à `no`
3. Sauvegardez
4. Attendez la prochaine synchronisation (ou lancez manuellement)
5. Le monitoring est désactivé dans Zabbix (pas d'alertes)
6. Après la maintenance, remettez `cf_monitoring` à `yes`
7. Le monitoring est réactivé

### Cas 2: Exclure des Devices du Monitoring

**Scénario**: Devices de test ou de développement

1. Lors de la création du device dans NetBox
2. Définissez `cf_monitoring = no`
3. Le device sera créé dans Zabbix mais désactivé
4. Aucune alerte ne sera générée

### Cas 3: Activation Progressive

**Scénario**: Déploiement de nouveaux serveurs

1. Créez les devices dans NetBox avec `cf_monitoring = no`
2. Configurez les serveurs
3. Une fois prêts, changez `cf_monitoring = yes`
4. Le monitoring s'active automatiquement

## 🔍 Vérification

### Dans NetBox:

```bash
# Via API - Lister les devices avec leur statut monitoring
curl -H "Authorization: Token VOTRE_TOKEN" \
  "http://localhost:8000/api/dcim/devices/?limit=100" | \
  jq '.results[] | {name: .name, monitoring: .custom_fields.cf_monitoring}'
```

### Dans Zabbix:

```bash
# Via Zabbix UI
Configuration → Hosts → Vérifier la colonne "Status"

# Enabled = Icône verte
# Disabled = Icône rouge
```

## 🛠️ Personnalisation

### Changer le Nom du Custom Field:

Si vous voulez utiliser un nom différent (par exemple `monitoring_enabled`):

1. Créez le custom field avec le nouveau nom dans NetBox
2. Dans le script `netbox_to_zabbix_sync.py`, modifiez:

```python
# Ligne 51
MONITORING_CUSTOM_FIELD = "monitoring_enabled"  # Votre nom
```

### Changer les Valeurs:

Si vous voulez utiliser `true/false` au lieu de `yes/no`:

1. Dans NetBox, créez le custom field avec les valeurs `true,false`
2. Dans le script, modifiez:

```python
# Lignes 52-53
MONITORING_ENABLED_VALUE = "true"    # Au lieu de "yes"
MONITORING_DISABLED_VALUE = "false"  # Au lieu de "no"
```

### Valeur par Défaut:

Pour changer le comportement par défaut (quand le champ n'est pas défini):

Dans le script, fonction `get_monitoring_status()`:

```python
# Ligne 168 - Pour désactiver par défaut au lieu d'activer
if cf_value is None:
    logger.debug(f"{device.name}: Custom field not set, defaulting to disabled")
    return 1  # Disabled au lieu de 0
```

## 📈 Workflow Complet

```
┌─────────────────────────────────────────┐
│        NetBox Device                    │
│  - Name: server-001                     │
│  - IP: 192.168.1.10                    │
│  - cf_monitoring: yes                  │
└──────────────┬──────────────────────────┘
               │
               │ Script sync
               │ (toutes les 15 min)
               │
               ▼
┌─────────────────────────────────────────┐
│       Lecture custom field              │
│  cf_monitoring = "yes"                  │
│  → status = 0 (ENABLED)                 │
└──────────────┬──────────────────────────┘
               │
               │ Zabbix API
               │ host.create/update
               │
               ▼
┌─────────────────────────────────────────┐
│        Zabbix Host                      │
│  - Name: server-001                     │
│  - IP: 192.168.1.10                    │
│  - Status: 0 (Enabled) ✅              │
│  - Monitoring: ACTIF                    │
└─────────────────────────────────────────┘
```

## 🎯 Résumé

✅ **Avantages**:
- Contrôle centralisé depuis NetBox
- Pas besoin d'accéder à Zabbix pour activer/désactiver
- Historique des changements dans NetBox
- Automatisation complète
- Synchronisation bidirectionnelle

✅ **Bonnes Pratiques**:
1. Définir `cf_monitoring = yes` par défaut
2. Documenter pourquoi un device est désactivé (commentaires NetBox)
3. Utiliser des tags NetBox pour grouper les devices désactivés
4. Planifier des revues régulières des devices désactivés
5. Logger les changements de statut

---

**Custom Field cf_monitoring**: Contrôle total du monitoring depuis NetBox! 🎉
