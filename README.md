# Plateforme de Monitoring et Analyse de Logs E-Commerce

## 📋 Description

Plateforme complète de centralisation, indexation et visualisation de logs pour une plateforme e-commerce traitant des milliers de commandes quotidiennes.

## 🏗️ Architecture

### Stack Technologique
- **Backend**: Flask (Python)
- **Indexation & Recherche**: Elasticsearch
- **Collecte de logs**: Logstash
- **Visualisation**: Kibana
- **Cache**: Redis
- **Base de données**: MongoDB
- **Conteneurisation**: Docker & Docker Compose

### Types de Logs Traités
1. **Logs de transactions** - Paiements, commandes, remboursements
2. **Logs d'erreurs applicatives** - Codes 404, 500, timeouts
3. **Logs de comportement utilisateur** - Navigation, paniers, abandons
4. **Logs de performance** - Temps de réponse API, latence BDD
5. **Logs de fraude** - Tentatives suspectes, détection de bots

## 🚀 Démarrage Rapide

### Prérequis (Windows)
- **Docker Desktop** pour Windows (avec WSL2 activé)
- **Python 3.11+** (version 3.13 recommandée)
- **PowerShell 5.1+** ou PowerShell Core
- **Git** pour Windows
- Au minimum **8 GB RAM** (16 GB recommandé pour l'ensemble des services)

### Installation

#### 1. Démarrer l'infrastructure Docker

```powershell
# Cloner le projet
git clone <repository-url>
cd projet_bigdata

# Démarrer tous les services avec Docker Compose
docker-compose up -d

# Vérifier que tous les services sont actifs (attendez ~30 secondes)
docker-compose ps
```

**Services démarrés** :
- Elasticsearch (port 9200) - Indexation et recherche
- Flask API (port 5001) - API REST ⚠️ **Port 5001 au lieu de 5000** (conflit résolu)
- Kibana (port 5601) - Visualisation
- Logstash (port 5000) - Collecte TCP/UDP
- MongoDB (port 27017) - Métadonnées
- Redis (port 6379) - Cache

#### 2. Configuration locale (optionnel - pour développement)

```powershell
# Créer un environnement virtuel Python
cd backend
python -m venv venv

# Activer l'environnement (PowerShell)
.\venv\Scripts\Activate.ps1

# Installer les dépendances minimales
pip install -r requirements-minimal.txt

# Lancer Flask en mode développement (port 5002)
$env:FLASK_APP="main.py"
python -m flask run --host=0.0.0.0 --port=5002
```

#### 3. Générer des logs de test

```powershell
# Générer 100 logs d'exemple
python scripts/generate_sample_logs.py -n 100

# Les logs sont créés dans scripts/sample_logs.json
```

#### 4. Initialiser Elasticsearch (optionnel)

```powershell
# Créer les index avec les mappings appropriés
python scripts/setup_elasticsearch.py
```

## 📁 Structure du Projet

```
projet_bigdata/
├── backend/                 # Application Flask
│   ├── app/
│   │   ├── routes/         # Endpoints API
│   │   ├── services/       # Logique métier
│   │   ├── models/         # Modèles de données
│   │   └── utils/          # Utilitaires
│   └── tests/              # Tests unitaires et d'intégration
├── infra/                  # Configuration infrastructure
│   ├── elasticsearch/
│   ├── logstash/
│   └── kibana/
├── scripts/                # Scripts d'automatisation
├── docs/                   # Documentation
└── uploads/                # Fichiers de logs uploadés
```

## 🔧 Configuration

Modifier le fichier `.env` avec vos paramètres :
- Configuration Elasticsearch
- Configuration MongoDB
- Configuration Redis
- Clés API et secrets

## 📊 Accès aux Services

- **Flask API (Docker)**: http://localhost:5001 ⚠️ **Port modifié de 5000 → 5001**
- **Flask API (Local Dev)**: http://localhost:5002
- **Kibana Dashboard**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200
- **Logstash TCP/UDP**: localhost:5000
- **Logstash API**: http://localhost:9600
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

### Endpoints API Principaux

```powershell
# Health check
Invoke-WebRequest "http://localhost:5001/health"

# Ingest logs (POST)
Invoke-WebRequest -Uri "http://localhost:5001/api/logs/ingest" `
  -Method POST -ContentType "application/json" `
  -Body '{"type":"transaction","data":{"order_id":"12345","amount":99.99}}'

# Récupérer logs récents
Invoke-WebRequest "http://localhost:5001/api/logs/recent?limit=10"

# Recherche full-text
Invoke-WebRequest "http://localhost:5001/api/search/?query=transaction"

# Dashboard overview
Invoke-WebRequest "http://localhost:5001/api/dashboard/overview"

# Types de logs disponibles
Invoke-WebRequest "http://localhost:5001/api/logs/types"
```

## 🧪 Tests

```powershell
# Activer l'environnement virtuel
cd backend
.\venv\Scripts\Activate.ps1

# Installer pytest si nécessaire
pip install pytest

# Lancer les tests
pytest tests/ -v

# Tests avec coverage
pytest tests/ --cov=app --cov-report=html
```

## 🐛 Dépannage

### Problèmes Courants

**1. Logstash ne démarre pas**
- Vérifiez le fichier de configuration `infra/logstash/pipelines/ecommerce-logs.conf`
- Testez la syntaxe : `docker run --rm -v "${PWD}/infra/logstash/pipelines:/usr/share/logstash/pipeline" docker.elastic.co/logstash/logstash:8.11.0 logstash -f /usr/share/logstash/pipeline/ecommerce-logs.conf --config.test_and_exit`

**2. Port 5000 déjà utilisé**
- Le port 5000 est réservé à Logstash (TCP/UDP)
- Flask utilise le port 5001 dans Docker
- Pour développement local, utilisez le port 5002

**3. Kibana affiche des warnings CSP**
- Ces warnings sont normaux en développement
- Message attendu : "Content Security Policy directive 'script-src 'self'"
- Kibana fonctionne malgré ces avertissements

**4. Elasticsearch import errors**
- Si erreur `ElasticsearchException`, c'est corrigé dans `app/services/elasticsearch_service.py`
- Utilisation de `Exception` au lieu de `ElasticsearchException` (API 8.11)

### Commandes de diagnostic

```powershell
# Vérifier l'état de tous les containers
docker-compose ps

# Logs d'un service spécifique
docker-compose logs flask-app --tail 50
docker-compose logs elasticsearch --tail 50
docker-compose logs logstash --tail 50

# Redémarrer un service
docker-compose restart flask-app

# Reconstruire et redémarrer
docker-compose down
docker-compose up -d --build

# Vérifier les index Elasticsearch
Invoke-WebRequest "http://localhost:9200/_cat/indices?v"

# Tester la connexion Elasticsearch
Invoke-WebRequest "http://localhost:9200/_cluster/health"
```

## 📖 Documentation

Consulter le dossier `docs/` pour :
- **architecture.md** - Architecture détaillée et flux de données
- **api_documentation.md** - Documentation complète des endpoints (20+ routes)
- **quick_start.md** - Guide de démarrage rapide
- **PROJECT_SUMMARY.md** - Résumé technique du projet

### Fonctionnalités Implémentées

✅ **Gestion des Logs**
- Ingestion via API REST (JSON)
- Ingestion via Logstash (TCP/UDP port 5000)
- Upload de fichiers logs
- Support de 5 types de logs (transaction, error, user_behavior, performance, fraud)

✅ **Recherche et Analytics**
- Recherche full-text avec Elasticsearch
- Autocomplétion
- Agrégations par type, période, statut
- Statistiques en temps réel

✅ **Dashboard**
- Vue d'ensemble 24h
- Métriques de performance
- Distribution des types de logs
- Alertes de fraude

✅ **Détection de Fraude**
- Scoring automatique (0-100)
- Détection d'activités suspectes
- 5 indicateurs de fraude

✅ **Performance Monitoring**
- Temps de réponse API
- Latence base de données
- Calcul de percentiles (p50, p95, p99)

## 🔧 Configuration Avancée

### Variables d'Environnement

Créer un fichier `.env` à la racine :

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=ecommerce_logs

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Logstash
LOGSTASH_HOST=localhost
LOGSTASH_PORT=5000
```

### Modifications Importantes Appliquées

**Corrections de Bugs** :
1. ✅ Port Flask changé de 5000 → 5001 (conflit avec Logstash)
2. ✅ Import Elasticsearch corrigé (`ElasticsearchException` → `Exception`)
3. ✅ Configuration Kibana mise à jour pour v8.11 (logging.appenders)
4. ✅ Fichier Logstash pipeline reconfiguré sans commentaires problématiques
5. ✅ Attribut `version` retiré de docker-compose.yml (obsolète)

**Optimisations** :
- Cache Redis configuré pour les requêtes
- Mappings Elasticsearch optimisés pour la recherche
- Geolocalization activée sur les IPs
- Pipeline Logstash avec enrichissement automatique

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT.

## 👥 Auteur

Équipe Infrastructure & Data Engineering
