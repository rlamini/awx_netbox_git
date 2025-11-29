# Guide d'Installation AWX avec Minikube / AWX with Minikube Installation Guide

## 📋 Qu'est-ce qu'AWX? / What is AWX?

AWX est la version open-source de Red Hat Ansible Tower, une interface web pour Ansible qui permet de:
- Gérer les inventaires dynamiques / Manage dynamic inventories
- Exécuter des playbooks Ansible / Run Ansible playbooks
- Planifier des jobs automatiques / Schedule automated jobs
- Contrôler l'accès basé sur les rôles (RBAC) / Role-based access control
- Visualiser les résultats en temps réel / Real-time results visualization
- Intégrer avec NetBox, Git, LDAP, etc.

AWX is the open-source version of Red Hat Ansible Tower, providing a web interface for Ansible with inventory management, playbook execution, job scheduling, RBAC, and integrations with NetBox, Git, LDAP, etc.

## 🆕 AWX Latest Version

AWX est développé activement avec des releases fréquentes:
- 🚀 Interface utilisateur moderne (AWX UI)
- 📊 Tableaux de bord et visualisations
- 🔌 API REST complète
- 🔒 Authentification avancée (LDAP, SAML, OAuth2)
- 📦 Inventaires dynamiques (NetBox, VMware, AWS, Azure, etc.)
- 🤖 Workflows et job templates
- 📈 Métriques et statistiques
- 🌐 Multi-tenancy

AWX features modern UI, dashboards, complete REST API, advanced authentication, dynamic inventories, workflows, job templates, metrics, and multi-tenancy.

## 🔧 Prérequis / Prerequisites

### Matériel / Hardware
- **CPU**: 2 cores minimum, 4 recommandé / 2 cores minimum, 4 recommended
- **RAM**: 4 Go minimum, 8 Go recommandé / 4GB minimum, 8GB recommended
- **Disk**: 20 Go minimum / 20GB minimum

### Logiciels / Software
- Ubuntu 20.04+ ou distribution Linux similaire
- Docker installé (voir DOCKER_INSTALLATION_UBUNTU.md)
- Connexion Internet / Internet connection
- Accès sudo / sudo access

## 📁 Étape 1 : Installer Minikube / Step 1: Install Minikube

Minikube crée un cluster Kubernetes local pour exécuter AWX.
Minikube creates a local Kubernetes cluster to run AWX.

```bash
# Télécharger Minikube / Download Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Installer Minikube / Install Minikube
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Vérifier l'installation / Verify installation
minikube version
```

## 📁 Étape 2 : Installer kubectl / Step 2: Install kubectl

kubectl est l'outil de ligne de commande pour Kubernetes.
kubectl is the Kubernetes command-line tool.

```bash
# Télécharger kubectl / Download kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Installer kubectl / Install kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Vérifier l'installation / Verify installation
kubectl version --client
```

## 🚀 Étape 3 : Démarrer Minikube / Step 3: Start Minikube

```bash
# Démarrer Minikube avec ressources suffisantes / Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker

# Vérifier le statut / Check status
minikube status

# Vérifier les nodes / Check nodes
kubectl get nodes
```

**Note:** Si vous avez moins de 8Go de RAM, utilisez `--memory=4096` (4Go minimum).

## 📦 Étape 4 : Installer l'AWX Operator / Step 4: Install AWX Operator

L'AWX Operator gère le déploiement d'AWX sur Kubernetes.
The AWX Operator manages AWX deployment on Kubernetes.

```bash
# Créer le namespace / Create namespace
kubectl create namespace awx

# Installer l'opérateur AWX / Install AWX Operator
kubectl apply -f https://raw.githubusercontent.com/ansible/awx-operator/devel/deploy/awx-operator.yaml -n awx

# Attendre que l'opérateur soit prêt / Wait for operator to be ready
kubectl wait --for=condition=available --timeout=300s deployment/awx-operator-controller-manager -n awx

# Vérifier le déploiement / Check deployment
kubectl get pods -n awx
```

## 📋 Étape 5 : Créer la Configuration AWX / Step 5: Create AWX Configuration

Créez un fichier `awx-instance.yaml`:
Create a file `awx-instance.yaml`:

```bash
cat > awx-instance.yaml <<EOF
---
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx
  namespace: awx
spec:
  service_type: NodePort
  nodeport_port: 30080

  # Ressources pour le web container / Resources for web container
  web_resource_requirements:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1000m
      memory: 2Gi

  # Ressources pour le task container / Resources for task container
  task_resource_requirements:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1000m
      memory: 2Gi

  # Configuration PostgreSQL / PostgreSQL configuration
  postgres_storage_class: standard
  postgres_storage_requirements:
    requests:
      storage: 8Gi

  # Configuration des projets / Projects configuration
  projects_persistence: true
  projects_storage_class: standard
  projects_storage_size: 8Gi

  # Admin par défaut / Default admin
  admin_user: admin
  admin_password_secret: awx-admin-password
EOF
```

## 🔐 Étape 6 : Créer le Secret Admin / Step 6: Create Admin Secret

```bash
# Générer un mot de passe fort / Generate strong password
ADMIN_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-24)

# Créer le secret / Create secret
kubectl create secret generic awx-admin-password \
  --from-literal=password="${ADMIN_PASSWORD}" \
  -n awx

# Sauvegarder le mot de passe / Save password
echo "AWX Admin Password: ${ADMIN_PASSWORD}" > awx-credentials.txt
echo "⚠️ IMPORTANT: Sauvegardez ce mot de passe en lieu sûr!"
echo "AWX Admin Password: ${ADMIN_PASSWORD}"
```

## 🎯 Étape 7 : Déployer AWX / Step 7: Deploy AWX

```bash
# Appliquer la configuration / Apply configuration
kubectl apply -f awx-instance.yaml -n awx

# Surveiller le déploiement / Monitor deployment
kubectl logs -f deployment/awx-operator-controller-manager -n awx

# Attendre que AWX soit prêt (peut prendre 5-10 minutes)
# Wait for AWX to be ready (may take 5-10 minutes)
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=awx -n awx --timeout=600s
```

**Vérifier le déploiement / Check deployment:**

```bash
# Voir tous les pods / See all pods
kubectl get pods -n awx

# Voir les services / See services
kubectl get svc -n awx

# Voir l'état AWX / See AWX status
kubectl get awx -n awx
```

## 🌐 Étape 8 : Accéder à AWX / Step 8: Access AWX

### Méthode 1 : NodePort (Local)

```bash
# Obtenir l'URL d'accès / Get access URL
minikube service awx-service -n awx --url

# Ou accéder directement / Or access directly
# http://localhost:30080
```

### Méthode 2 : Port Forward

```bash
# Port forward (en arrière-plan) / Port forward (background)
kubectl port-forward svc/awx-service 8080:80 -n awx &

# Accéder / Access
# http://localhost:8080
```

### Méthode 3 : Minikube Tunnel (pour exposer sur Internet)

```bash
# Créer un tunnel / Create tunnel
minikube tunnel
```

## 👤 Étape 9 : Première Connexion / Step 9: First Login

1. Ouvrez votre navigateur / Open your browser
2. Accédez à l'URL AWX / Navigate to AWX URL
3. Connectez-vous / Login:
   - **Username**: `admin`
   - **Password**: (voir awx-credentials.txt / see awx-credentials.txt)

## 📊 Étape 10 : Configuration Initiale / Step 10: Initial Configuration

### 1. Configurer une Organisation / Configure Organization

1. Allez dans **Organizations**
2. Cliquez sur **Add**
3. Nom: `Mon Organisation`
4. Sauvegardez / Save

### 2. Ajouter un Inventaire / Add Inventory

1. Allez dans **Inventories**
2. Cliquez sur **Add** → **Add inventory**
3. Nom: `Mon Inventaire`
4. Organisation: `Mon Organisation`
5. Sauvegardez / Save

### 3. Ajouter des Credentials / Add Credentials

1. Allez dans **Credentials**
2. Cliquez sur **Add**
3. Types disponibles:
   - Machine (SSH)
   - Source Control (Git)
   - Network
   - Cloud (AWS, Azure, GCP)
   - NetBox

### 4. Ajouter un Projet / Add Project

1. Allez dans **Projects**
2. Cliquez sur **Add**
3. Configurez:
   - Nom: `Mon Projet`
   - Organisation: `Mon Organisation`
   - SCM Type: `Git`
   - SCM URL: `https://github.com/votre-repo/playbooks.git`
4. Sauvegardez / Save

### 5. Créer un Job Template / Create Job Template

1. Allez dans **Templates**
2. Cliquez sur **Add** → **Add job template**
3. Configurez:
   - Nom: `Mon Job`
   - Job Type: `Run`
   - Inventory: `Mon Inventaire`
   - Project: `Mon Projet`
   - Playbook: Sélectionnez votre playbook
   - Credentials: Sélectionnez vos credentials
4. Sauvegardez / Save
5. Cliquez sur **Launch** pour exécuter

## 🔌 Intégration avec NetBox / NetBox Integration

AWX peut utiliser NetBox comme source d'inventaire dynamique.
AWX can use NetBox as a dynamic inventory source.

### 1. Créer un Token NetBox / Create NetBox Token

Dans NetBox:
1. Allez dans **Admin** → **API Tokens**
2. Créez un nouveau token
3. Copiez le token

### 2. Ajouter NetBox Credentials dans AWX

1. Dans AWX, allez dans **Credentials**
2. Cliquez sur **Add**
3. Configurez:
   - Name: `NetBox Credentials`
   - Credential Type: `Red Hat Ansible Automation Platform`
   - Token: `votre_token_netbox`
4. Sauvegardez

### 3. Créer un Inventaire NetBox / Create NetBox Inventory

1. Allez dans **Inventories**
2. Cliquez sur **Add** → **Add inventory**
3. Nom: `NetBox Inventory`
4. Sauvegardez
5. Allez dans l'onglet **Sources**
6. Cliquez sur **Add**
7. Configurez:
   - Name: `NetBox Source`
   - Source: `NetBox`
   - Credential: `NetBox Credentials`
   - NetBox URL: `https://netbox.example.com`
8. Sauvegardez et synchronisez

### 4. Exemple de Playbook avec NetBox

```yaml
---
- name: Configuration des serveurs depuis NetBox
  hosts: all
  gather_facts: yes
  tasks:
    - name: Afficher les informations NetBox
      debug:
        msg: "Serveur {{ inventory_hostname }} depuis NetBox"

    - name: Installer les packages
      apt:
        name: "{{ packages }}"
        state: present
      when: ansible_os_family == "Debian"
```

## 🔧 Commandes Utiles / Useful Commands

### Gestion Minikube / Minikube Management

```bash
# Arrêter Minikube / Stop Minikube
minikube stop

# Démarrer Minikube / Start Minikube
minikube start

# Supprimer Minikube / Delete Minikube
minikube delete

# Voir les ressources / See resources
minikube dashboard

# Voir les logs / View logs
minikube logs
```

### Gestion AWX / AWX Management

```bash
# Voir les pods AWX / View AWX pods
kubectl get pods -n awx

# Voir les logs AWX / View AWX logs
kubectl logs -f deployment/awx-web -n awx

# Voir les logs PostgreSQL / View PostgreSQL logs
kubectl logs -f deployment/awx-postgres-13 -n awx

# Redémarrer AWX / Restart AWX
kubectl rollout restart deployment/awx-web -n awx
kubectl rollout restart deployment/awx-task -n awx

# Voir les événements / View events
kubectl get events -n awx --sort-by='.lastTimestamp'

# Accéder au shell AWX / Access AWX shell
kubectl exec -it deployment/awx-web -n awx -- /bin/bash
```

### Sauvegarder AWX / Backup AWX

```bash
# Sauvegarder la base de données / Backup database
kubectl exec -n awx deployment/awx-postgres-13 -- pg_dump -U awx awx > awx_backup_$(date +%Y%m%d).sql

# Sauvegarder les configurations / Backup configurations
kubectl get awx awx -n awx -o yaml > awx_config_backup.yaml
```

### Mettre à jour AWX / Update AWX

```bash
# Mettre à jour l'opérateur / Update operator
kubectl apply -f https://raw.githubusercontent.com/ansible/awx-operator/devel/deploy/awx-operator.yaml -n awx

# Attendre la mise à jour / Wait for update
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=awx -n awx --timeout=600s
```

## 🌐 Exposer AWX sur Internet / Expose AWX to Internet

### Option 1 : Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name awx.example.com;

    location / {
        proxy_pass http://localhost:30080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Puis SSL avec Let's Encrypt:
```bash
sudo certbot --nginx -d awx.example.com
```

### Option 2 : Ingress Kubernetes

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: awx-ingress
  namespace: awx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - awx.example.com
    secretName: awx-tls
  rules:
  - host: awx.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: awx-service
            port:
              number: 80
```

## 🛠️ Dépannage / Troubleshooting

### AWX ne démarre pas / AWX Won't Start

```bash
# Vérifier les logs de l'opérateur / Check operator logs
kubectl logs -f deployment/awx-operator-controller-manager -n awx

# Vérifier les pods / Check pods
kubectl get pods -n awx
kubectl describe pod <pod-name> -n awx

# Vérifier les événements / Check events
kubectl get events -n awx --sort-by='.lastTimestamp'
```

### Problème de ressources / Resource Issues

```bash
# Augmenter les ressources Minikube / Increase Minikube resources
minikube stop
minikube start --cpus=4 --memory=8192 --disk-size=30g

# Vérifier l'utilisation / Check usage
kubectl top nodes
kubectl top pods -n awx
```

### Base de données corrompue / Database Corrupted

```bash
# Supprimer et recréer AWX / Delete and recreate AWX
kubectl delete awx awx -n awx
kubectl apply -f awx-instance.yaml -n awx
```

### Réinitialisation complète / Complete Reset

```bash
# Supprimer AWX / Delete AWX
kubectl delete namespace awx

# Recréer / Recreate
kubectl create namespace awx
kubectl apply -f https://raw.githubusercontent.com/ansible/awx-operator/devel/deploy/awx-operator.yaml -n awx
kubectl apply -f awx-instance.yaml -n awx
```

## 📈 Optimisation des Performances / Performance Optimization

### Pour Production / For Production

```yaml
# Dans awx-instance.yaml
spec:
  # Augmenter les ressources / Increase resources
  web_resource_requirements:
    requests:
      cpu: 1000m
      memory: 2Gi
    limits:
      cpu: 2000m
      memory: 4Gi

  task_resource_requirements:
    requests:
      cpu: 1000m
      memory: 2Gi
    limits:
      cpu: 2000m
      memory: 4Gi

  # Plus de stockage / More storage
  postgres_storage_requirements:
    requests:
      storage: 20Gi

  projects_storage_size: 20Gi

  # Replicas pour haute disponibilité / Replicas for HA
  replicas: 2
```

## 📚 Ressources / Resources

- [AWX Official Documentation](https://ansible.readthedocs.io/projects/awx/en/latest/)
- [AWX Operator GitHub](https://github.com/ansible/awx-operator)
- [AWX GitHub](https://github.com/ansible/awx)
- [Ansible Documentation](https://docs.ansible.com/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## 💡 Bonnes Pratiques / Best Practices

### Sécurité / Security

1. ✅ Changez le mot de passe admin
2. ✅ Utilisez HTTPS (SSL/TLS)
3. ✅ Activez l'authentification LDAP/SAML
4. ✅ Utilisez des credentials séparés par environnement
5. ✅ Limitez l'accès par RBAC
6. ✅ Sauvegardez régulièrement
7. ✅ Auditez les logs

### Organisation / Organization

1. ✅ Organisez les projets par équipe
2. ✅ Utilisez des organisations pour la multi-tenancy
3. ✅ Standardisez les noms de job templates
4. ✅ Documentez vos playbooks
5. ✅ Versionnez vos playbooks dans Git
6. ✅ Utilisez des inventaires dynamiques
7. ✅ Créez des workflows pour les tâches complexes

### Performances / Performance

1. ✅ Limitez le parallélisme des jobs
2. ✅ Optimisez vos playbooks Ansible
3. ✅ Utilisez des facts gathering selectifs
4. ✅ Nettoyez les anciens jobs régulièrement
5. ✅ Surveillez l'utilisation des ressources

## 🎓 Prochaines Étapes / Next Steps

Après l'installation:
1. Changez le mot de passe admin
2. Configurez votre organisation
3. Ajoutez vos credentials
4. Connectez vos projets Git
5. Créez vos inventaires
6. Importez vos playbooks
7. Créez vos job templates
8. Testez l'exécution de jobs
9. Configurez les notifications
10. Intégrez avec NetBox (inventaire dynamique)
11. Planifiez des jobs automatiques
12. Configurez les workflows

---

**Ansible AWX** : L'automatisation IT simplifiée! 🎉

**Ansible AWX**: IT automation made simple! 🎉
