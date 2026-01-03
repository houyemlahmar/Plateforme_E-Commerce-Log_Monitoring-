# Architecture Documentation

## Vue d'ensemble

La plateforme de monitoring et d'analyse de logs e-commerce est construite avec une architecture microservices moderne et sécurisée utilisant les technologies suivantes :

### Stack Technologique

#### Backend
- **Flask 3.0** : Framework web Python léger et flexible
- **Python 3.11** : Langage de programmation principal
- **Gunicorn** : Serveur WSGI pour la production
- **PyJWT 2.8.0** : 🔐 Authentification JWT (JSON Web Tokens)
- **bcrypt** : 🔐 Hachage sécurisé des mots de passe (12 rounds)

#### Stack ELK
- **Elasticsearch 8.11** : Moteur de recherche et d'indexation
- **Logstash 8.11** : Pipeline de traitement des logs
- **Kibana 8.11** : Interface de visualisation

#### Bases de données
- **MongoDB 7.0** : Stockage des métadonnées + 🔐 collection users
- **Redis 7.2** : Cache, sessions et queue jobs

#### Conteneurisation
- **Docker** : Conteneurisation des services
- **Docker Compose** : Orchestration multi-conteneurs (8 services)

## Architecture des Services

### 1. Application Flask (Backend)

L'application Flask est organisée selon les principes de la clean architecture avec couche de sécurité JWT :

```
backend/
├── app/
│   ├── routes/          # 7 modules de routes API
│   │   ├── auth_routes.py      # 🔐 11 endpoints authentification
│   │   ├── user_routes.py      # 🔐 CRUD utilisateurs
│   │   ├── log_routes.py       # Upload & ingestion
│   │   ├── analytics_routes.py # Métriques agrégées
│   │   ├── dashboard_routes.py # Stats et visualisations
│   │   ├── fraud_routes.py     # Détection fraude
│   │   └── search_routes.py    # Recherche avancée
│   ├── services/        # 10 services métier
│   │   ├── auth_service.py     # 🔐 Login & tokens
│   │   ├── user_repository.py  # 🔐 MongoDB users
│   │   └── ...
│   ├── models/          # 4 modèles de données
│   │   ├── user.py             # 🔐 User model avec rôles
│   │   └── ...
│   ├── utils/           # 4 modules utilitaires
│   │   ├── jwt_utils.py        # 🔐 Decorators JWT
│   │   └── ...
│   └── templates/       # 8 templates HTML avec auth JS
├── config.py            # 🔐 Configuration (JWT, MongoDB, etc.)
└── main.py              # Point d'entrée
```

#### Routes API

- 🔐 **/api/auth** : Authentification JWT (login, register, refresh, logout, me)
- 🔐 **/api/users** : Gestion utilisateurs (CRUD avec contrôle de rôle)
- **/api/logs** : Gestion des logs (upload, ingestion, recherche) [Analyst+]
- **/api/analytics** : Analyses et métriques [Analyst+]
- **/api/dashboard** : Données pour le tableau de bord [Viewer+]
- **/api/fraud** : Détection de fraude [Analyst+]
- **/api/search** : Recherche avancée avec sauvegarde [Analyst+]
- **/api/search** : Recherche avancée

#### Services

- **ElasticsearchService** : Interface avec Elasticsearch
- **MongoDBService** : Interface avec MongoDB
- **RedisService** : Gestion du cache
- **LogService** : Traitement des logs
- **AnalyticsService** : Calculs analytiques
- **FraudDetectionService** : Détection de fraude
- **PerformanceService** : Monitoring de performance
- **SearchService** : Recherche dans les logs

### 2. Elasticsearch

Elasticsearch indexe et stocke tous les logs pour une recherche ultra-rapide.

#### Index Structure

```
ecommerce-logs-YYYY.MM.DD/
├── transaction logs
├── error logs
├── user behavior logs
├── performance logs
└── fraud detection logs
```

#### Mappings

Chaque type de log possède son propre mapping optimisé pour la recherche et l'agrégation.

### 3. Logstash

Logstash collecte, transforme et enrichit les logs avant de les indexer dans Elasticsearch.

#### Pipeline

1. **Input** : TCP/UDP ports, Beats
2. **Filter** : Parsing JSON, enrichissement géolocalisation, conversion types
3. **Output** : Elasticsearch

### 4. Kibana

Kibana fournit une interface de visualisation pour :

- Exploration des logs
- Création de dashboards
- Alertes et monitoring
- Recherche avancée

### 5. MongoDB

MongoDB stocke les métadonnées et informations non searchables :

- Fichiers de logs uploadés
- Historique des détections de fraude
- Sessions utilisateurs
- Configuration

### 6. Redis

Redis gère :

- Cache des requêtes fréquentes
- Sessions utilisateurs
- Compteurs en temps réel
- Files d'attente

## Flux de Données

### 1. Ingestion de Logs

```
Client → Flask API → Validation → Logstash → Elasticsearch
                    ↓
                MongoDB (métadonnées)
```

### 2. Recherche de Logs

```
Client → Flask API → Redis (cache) → Elasticsearch → Response
```

### 3. Détection de Fraude

```
Transaction Log → Fraud Service → Analyse → MongoDB + Elasticsearch
                                    ↓
                                Alerte si fraude détectée
```

## Scalabilité

### Horizontal Scaling

- **Flask** : Multiple workers via Gunicorn
- **Elasticsearch** : Cluster multi-nœuds
- **Redis** : Redis Cluster ou Sentinel
- **MongoDB** : Replica sets

### Vertical Scaling

- Augmentation des ressources CPU/RAM
- Optimisation des index Elasticsearch
- Tuning des configurations

## Sécurité

### Authentification & Autorisation

- JWT tokens pour l'API
- RBAC (Role-Based Access Control)

### Chiffrement

- TLS/SSL pour communications
- Chiffrement des données sensibles

### Monitoring

- Logs d'audit
- Détection d'anomalies
- Alertes automatiques

## Performance

### Optimisations

1. **Cache Redis** : Réduction de 80% des requêtes Elasticsearch
2. **Index Elasticsearch** : Recherches sub-secondes
3. **Bulk operations** : Traitement par batch
4. **Pagination** : Limitation des résultats

### Métriques

- Response time < 200ms (P95)
- Throughput : 1000 logs/seconde
- Disponibilité : 99.9%

## Déploiement

### Environnements

- **Development** : Docker Compose local
- **Staging** : Kubernetes cluster
- **Production** : Kubernetes avec haute disponibilité

### CI/CD

1. Tests automatiques (pytest)
2. Build Docker images
3. Push vers registry
4. Déploiement automatique

## Maintenance

### Monitoring

- Health checks automatiques
- Métriques via Prometheus
- Dashboards Grafana
- Alertes PagerDuty

### Backup

- Snapshots Elasticsearch quotidiens
- Backup MongoDB incrémentiels
- Rétention 90 jours

### Logs Rotation

- Rotation quotidienne
- Compression après 7 jours
- Suppression après 90 jours
