# Guide d'Exposition AWX sur Internet / AWX Internet Access Guide

## 📋 Vue d'ensemble / Overview

Ce guide explique comment exposer AWX (installé avec Minikube sur un VPS) **directement** sur Internet **sans Nginx**, en utilisant simplement une redirection de port.

This guide explains how to expose AWX (installed with Minikube on a VPS) **directly** to the Internet **without Nginx**, using simple port redirection.

## 🔧 Prérequis / Prerequisites

- ✅ AWX installé sur VPS avec Minikube (voir AWX_MINIKUBE_SETUP.md)
- ✅ VPS avec IP publique
- ✅ (Optionnel) Nom de domaine configuré pointant vers l'IP du VPS
- ✅ Port 80 ouvert sur le firewall
- ✅ Accès root/sudo au VPS

## 🚀 Solution Simple: Redirection de Port

AWX est accessible sur le NodePort `30080`. Pour l'exposer sur Internet via le port 80, on redirige simplement le port 80 vers 30080.

### Étape 1: Vérifier AWX

```bash
# Vérifier que AWX fonctionne
kubectl get pods -n awx
kubectl get svc -n awx

# Tester l'accès local
curl http://localhost:30080
```

Vous devriez voir le service AWX:
```
NAME          TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
awx-service   NodePort   10.96.x.x       <none>        80:30080/TCP   10m
```

### Étape 2: Configurer iptables pour rediriger le port 80

```bash
# Rediriger le port 80 vers 30080
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 30080

# Vérifier la règle
sudo iptables -t nat -L PREROUTING -n -v | grep 30080
```

### Étape 3: Rendre la règle persistante

```bash
# Installer iptables-persistent pour sauvegarder les règles
sudo apt update
sudo apt install iptables-persistent -y

# Sauvegarder les règles actuelles
sudo netfilter-persistent save

# Ou manuellement:
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

### Étape 4: Ouvrir le port 80 dans le firewall

#### Avec UFW:
```bash
# Autoriser le port 80
sudo ufw allow 80/tcp

# Vérifier
sudo ufw status
```

#### Avec iptables direct:
```bash
# Autoriser le port 80
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# Sauvegarder
sudo netfilter-persistent save
```

#### Sur votre fournisseur cloud:
N'oubliez pas d'ouvrir le port 80 dans le panneau de configuration de votre fournisseur (OVH, DigitalOcean, AWS, etc.)

### Étape 5: Tester l'accès depuis Internet

```bash
# Depuis votre VPS
curl http://localhost

# Depuis votre machine locale (remplacez par l'IP publique du VPS)
curl http://VOTRE_IP_PUBLIQUE

# Ou dans le navigateur
http://VOTRE_IP_PUBLIQUE
```

Si vous avez un nom de domaine:
```bash
http://awx.example.com
```

## ✅ C'est tout! AWX est maintenant accessible

Vous pouvez maintenant accéder à AWX:
- **Par IP**: `http://VOTRE_IP_PUBLIQUE`
- **Par domaine**: `http://awx.example.com` (si configuré)
- **Username**: `admin`
- **Password**: (voir awx-credentials.txt)

## 🔒 (Optionnel) Ajouter HTTPS avec un certificat auto-signé

Si vous voulez HTTPS sans Nginx (moins recommandé):

### 1. Générer un certificat auto-signé

```bash
# Créer le répertoire pour les certificats
mkdir -p ~/awx-certs
cd ~/awx-certs

# Générer le certificat
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout awx-key.pem \
  -out awx-cert.pem \
  -subj "/C=FR/ST=IDF/L=Paris/O=MyCompany/CN=awx.example.com"
```

### 2. Créer un Secret Kubernetes

```bash
# Créer le secret TLS
kubectl create secret tls awx-tls-cert \
  --cert=~/awx-certs/awx-cert.pem \
  --key=~/awx-certs/awx-key.pem \
  -n awx
```

### 3. Modifier awx-instance.yaml

```yaml
---
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx
  namespace: awx
spec:
  service_type: NodePort
  nodeport_port: 30080

  # Ajouter SSL
  ingress_type: none
  service_tls_secret: awx-tls-cert

  # ... reste de la config
```

### 4. Appliquer et rediriger le port 443

```bash
# Appliquer la config
kubectl apply -f awx-instance.yaml -n awx

# Rediriger le port 443 vers 30443
sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 30443

# Sauvegarder
sudo netfilter-persistent save

# Ouvrir le port 443
sudo ufw allow 443/tcp
```

⚠️ **Note**: Avec un certificat auto-signé, vous aurez un avertissement de sécurité dans le navigateur.

## 🔧 Commandes Utiles

### Voir les règles iptables

```bash
# Voir toutes les règles NAT
sudo iptables -t nat -L -n -v

# Voir les redirections de port
sudo iptables -t nat -L PREROUTING -n -v
```

### Supprimer une règle iptables

```bash
# Lister avec numéros de ligne
sudo iptables -t nat -L PREROUTING --line-numbers

# Supprimer la règle (remplacez X par le numéro)
sudo iptables -t nat -D PREROUTING X

# Sauvegarder
sudo netfilter-persistent save
```

### Vérifier les ports ouverts

```bash
# Voir tous les ports en écoute
sudo ss -tulpn | grep LISTEN

# Vérifier le port 30080
sudo ss -tulpn | grep 30080

# Vérifier depuis l'extérieur
nc -zv VOTRE_IP_PUBLIQUE 80
```

### Voir les logs AWX

```bash
# Logs du conteneur web
kubectl logs -f deployment/awx-web -n awx

# Logs du conteneur task
kubectl logs -f deployment/awx-task -n awx

# Tous les pods
kubectl get pods -n awx
```

## 🛠️ Dépannage / Troubleshooting

### Problème: Connection refused

```bash
# Vérifier que AWX est bien démarré
kubectl get pods -n awx

# Tester l'accès local
curl http://localhost:30080

# Vérifier les règles iptables
sudo iptables -t nat -L PREROUTING -n -v | grep 30080

# Vérifier le firewall
sudo ufw status
sudo iptables -L INPUT -n -v | grep 80
```

### Problème: Timeout

```bash
# Vérifier que le port est ouvert sur le VPS
sudo ss -tulpn | grep :80

# Vérifier le firewall cloud (OVH, AWS, etc.)
# Aller dans le panneau de configuration et ouvrir le port 80

# Tester depuis l'extérieur
telnet VOTRE_IP_PUBLIQUE 80
```

### Problème: Règle iptables ne persiste pas après reboot

```bash
# Réinstaller iptables-persistent
sudo apt install --reinstall iptables-persistent

# Sauvegarder manuellement
sudo iptables-save > /etc/iptables/rules.v4

# Ou ajouter dans /etc/rc.local
sudo nano /etc/rc.local

# Ajouter avant "exit 0":
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 30080
```

## 📊 Architecture Finale

```
Internet (Port 80)
        ↓
   Firewall VPS
        ↓
iptables REDIRECT (80 → 30080)
        ↓
Minikube NodePort (30080)
        ↓
  AWX Service (80)
        ↓
    AWX Pods
```

## 🔐 Recommandations de Sécurité

### 1. Changer le mot de passe admin

```bash
# Connexion à AWX
# Settings → Users → admin → Edit → Change password
```

### 2. Limiter l'accès par IP (iptables)

```bash
# Autoriser seulement une IP spécifique
sudo iptables -I INPUT -p tcp --dport 80 ! -s VOTRE_IP_BUREAU -j DROP

# Ou autoriser un sous-réseau
sudo iptables -I INPUT -p tcp --dport 80 -s 203.0.113.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j DROP

# Sauvegarder
sudo netfilter-persistent save
```

### 3. Installer fail2ban

```bash
# Installer fail2ban
sudo apt install fail2ban -y

# Créer une jail pour AWX
sudo tee /etc/fail2ban/jail.d/awx.conf <<EOF
[awx]
enabled = true
port = 80
filter = awx
logpath = /var/log/syslog
maxretry = 5
bantime = 3600
EOF

# Redémarrer
sudo systemctl restart fail2ban
```

### 4. Monitoring des connexions

```bash
# Voir les connexions actives
sudo netstat -tn | grep :80

# Voir les IPs qui se connectent
sudo tail -f /var/log/syslog | grep AWX
```

## 🎯 Checklist de Déploiement

- [ ] AWX installé et fonctionnel (`kubectl get pods -n awx`)
- [ ] Service AWX de type NodePort sur port 30080
- [ ] Règle iptables créée (port 80 → 30080)
- [ ] Règle iptables persistante après reboot
- [ ] Firewall VPS ouvert sur port 80
- [ ] Firewall cloud ouvert sur port 80 (si applicable)
- [ ] Accès local testé (`curl http://localhost`)
- [ ] Accès Internet testé (depuis votre machine)
- [ ] Connexion AWX testée (admin login)
- [ ] Mot de passe admin changé
- [ ] (Optionnel) Nom de domaine configuré
- [ ] (Optionnel) HTTPS configuré
- [ ] (Optionnel) fail2ban installé

## 🎉 Accès Final

AWX est maintenant accessible sur Internet:

- **URL par IP**: `http://VOTRE_IP_PUBLIQUE`
- **URL par domaine**: `http://awx.example.com` (si configuré)
- **Username**: `admin`
- **Password**: (voir awx-credentials.txt)

## 📝 Commande Complète (Copier-Coller)

```bash
# Installation complète en une seule fois
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 30080
sudo apt install iptables-persistent -y
sudo netfilter-persistent save
sudo ufw allow 80/tcp
echo "✅ AWX est maintenant accessible sur http://$(curl -s ifconfig.me)"
```

---

**AWX sur Internet** : Simple, Direct, Accessible! 🚀

**AWX on Internet**: Simple, Direct, Accessible! 🚀
