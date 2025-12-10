# 📊 Plateforme de Monitoring et Analyse de Logs E-Commerce
## Projet Big Data - Flask + ELK Stack + MongoDB + Redis

---

## ✅ Structure Complète du Projet

```
projet_bigdata/
├── 📁 backend/                      # Application Flask
│   ├── 📁 app/
│   │   ├── 📁 routes/              # 6 modules de routes API
│   │   │   ├── logs_routes.py
│   │   │   ├── analytics_routes.py
│   │   │   ├── dashboard_routes.py
│   │   │   ├── fraud_routes.py
│   │   │   ├── performance_routes.py
│   │   │   └── search_routes.py
│   │   │
│   │   ├── 📁 services/            # 9 services métier
│   │   │   ├── elasticsearch_service.py
│   │   │   ├── mongodb_service.py
│   │   │   ├── redis_service.py
│   │   │   ├── log_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── fraud_service.py
│   │   │   ├── performance_service.py
│   │   │   └── search_service.py
│   │   │
│   │   ├── 📁 models/              # 3 modèles de données
│   │   │   ├── log_model.py
│   │   │   ├── transaction_model.py
│   │   │   └── fraud_model.py
│   │   │
│   │   └── 📁 utils/               # 3 modules utilitaires
│   │       ├── validators.py
│   │       ├── formatters.py
│   │       └── helpers.py
│   │
│   ├── 📁 tests/                   # Suite de tests complète
│   │   ├── conftest.py
│   │   ├── test_routes.py
│   │   ├── test_models.py
│   │   └── test_utils.py
│   │
│   ├── config.py                   # Configuration centralisée
│   ├── main.py                     # Point d'entrée
│   ├── requirements.txt            # Dépendances Python
│   ├── Dockerfile                  # Conteneurisation
│   └── pytest.ini                  # Configuration tests
│
├── 📁 infra/                        # Infrastructure ELK + MongoDB
│   ├── 📁 elasticsearch/
│   │   └── config/elasticsearch.yml
│   │
│   ├── 📁 logstash/
│   │   ├── config/logstash.yml
│   │   └── pipelines/ecommerce-logs.conf
│   │
│   ├── 📁 kibana/
│   │   └── config/kibana.yml
│   │
│   └── 📁 mongodb/
│       └── init-mongo.js
│
├── 📁 scripts/                      # Scripts utilitaires
│   ├── generate_sample_logs.py     # Générateur de logs de test
│   └── setup_elasticsearch.py      # Initialisation Elasticsearch
│
├── 📁 docs/                         # Documentation complète
│   ├── architecture.md             # Architecture technique
│   ├── api_documentation.md        # Documentation API
│   └── quick_start.md              # Guide de démarrage
│
├── 📁 uploads/                      # Dossier pour fichiers uploadés
│
├── docker-compose.yml              # Orchestration des services
├── .env.example                    # Template de configuration
├── .gitignore                      # Fichiers ignorés par Git
└── README.md                       # Documentation principale

```

---

## 🎯 Fonctionnalités Implémentées

### 1. Gestion des Logs
- ✅ Upload de fichiers de logs
- ✅ Ingestion JSON via API
- ✅ Support de 5 types de logs :
  - Transactions (paiements, commandes, remboursements)
  - Erreurs applicatives (404, 500, timeouts)
  - Comportement utilisateur (navigation, paniers, abandons)
  - Performance (temps de réponse API, latence BDD)
  - Fraude (tentatives suspectes, détection de bots)

### 2. Analytics Avancés
- ✅ Analytics de transactions (timeline, méthodes de paiement, statuts)
- ✅ Analytics d'erreurs (codes, types, chronologie)
- ✅ Analytics comportement utilisateur
- ✅ Analyse de tendances
- ✅ Métriques en temps réel

### 3. Détection de Fraude
- ✅ Scoring de fraude (0-100)
- ✅ Détection d'indicateurs multiples :
  - Montants élevés
  - Transactions rapides successives
  - Localisation suspecte
  - Tentatives échouées multiples
  - Mismatch IP
- ✅ Historique des détections
- ✅ Statistiques de fraude

### 4. Monitoring de Performance
- ✅ Temps de réponse API
- ✅ Latence base de données
- ✅ Percentiles (P50, P90, P95, P99)
- ✅ Requêtes lentes
- ✅ Analyse par endpoint

### 5. Recherche Puissante
- ✅ Recherche full-text dans Elasticsearch
- ✅ Filtres avancés (type, date, etc.)
- ✅ Highlighting des résultats
- ✅ Autocomplétion
- ✅ Recherche floue (fuzzy)

### 6. Dashboard & Visualisation
- ✅ Vue d'ensemble des métriques clés
- ✅ Graphiques temporels
- ✅ Distribution des types de logs
- ✅ Alertes fraude
- ✅ Données temps réel

---

## 🚀 Technologies Utilisées

### Backend
- **Flask 3.0** - Framework web Python
- **Python 3.11** - Langage principal
- **Gunicorn** - Serveur WSGI production

### Stack ELK
- **Elasticsearch 8.11** - Recherche et indexation
- **Logstash 8.11** - Pipeline de traitement
- **Kibana 8.11** - Visualisation

### Bases de Données
- **MongoDB 7.0** - Stockage métadonnées
- **Redis 7** - Cache et sessions

### Infrastructure
- **Docker & Docker Compose** - Conteneurisation
- **Nginx** (optionnel) - Reverse proxy

### Tests & Qualité
- **Pytest** - Framework de tests
- **Pytest-cov** - Couverture de code
- **Flake8** - Linting

---

## 📈 Métriques du Projet

### Code
- **~5,000 lignes** de code Python
- **27 fichiers** Python
- **6 routes** API principales
- **9 services** métier
- **3 modèles** de données
- **15+ tests** unitaires

### Infrastructure
- **6 services** Docker
- **4 configurations** ELK Stack
- **1 pipeline** Logstash
- **3 bases** de données

### Documentation
- **3 documents** markdown détaillés
- **20+ endpoints** API documentés
- **Guide** de démarrage rapide
- **Architecture** complète

---

## 🎯 Types de Logs Traités

### 1. 💰 Logs de Transactions
```json
{
  "log_type": "transaction",
  "transaction_id": "TXN12345",
  "user_id": "USER123",
  "amount": 150.00,
  "currency": "USD",
  "payment_method": "credit_card",
  "status": "completed"
}
```

### 2. ❌ Logs d'Erreurs
```json
{
  "log_type": "error",
  "error_code": 500,
  "error_type": "InternalServerError",
  "error_message": "Database connection failed",
  "endpoint": "/api/users"
}
```

### 3. 👤 Logs Comportement Utilisateur
```json
{
  "log_type": "user_behavior",
  "user_id": "USER123",
  "action": "add_to_cart",
  "page": "/products",
  "session_id": "SESSION123456"
}
```

### 4. ⚡ Logs de Performance
```json
{
  "log_type": "performance",
  "endpoint": "/api/products",
  "response_time": 250.5,
  "db_query_time": 50.2,
  "status_code": 200
}
```

### 5. 🚨 Logs de Fraude
```json
{
  "log_type": "fraud",
  "transaction_id": "TXN99999",
  "fraud_score": 85,
  "fraud_detected": true,
  "indicators": ["high_amount", "suspicious_location"]
}
```

---

## 🔧 Configuration Rapide

### 1. Démarrer le projet

```powershell
# Copier la configuration
Copy-Item .env.example .env

# Lancer tous les services
docker-compose up -d

# Vérifier l'état
docker-compose ps
```

### 2. Initialiser Elasticsearch

```powershell
cd scripts
python setup_elasticsearch.py
```

### 3. Générer des logs de test

```powershell
python generate_sample_logs.py -n 1000
```

### 4. Accéder aux interfaces

- **API Flask** : http://localhost:5000
- **Kibana** : http://localhost:5601
- **Elasticsearch** : http://localhost:9200

---

## 📊 Endpoints API Principaux

### Logs
- `POST /api/logs/upload` - Upload fichier
- `POST /api/logs/ingest` - Ingestion JSON
- `GET /api/logs/recent` - Logs récents
- `GET /api/logs/stats` - Statistiques

### Analytics
- `GET /api/analytics/transactions` - Analytics transactions
- `GET /api/analytics/errors` - Analytics erreurs
- `GET /api/analytics/trends` - Tendances

### Dashboard
- `GET /api/dashboard/overview` - Vue d'ensemble
- `GET /api/dashboard/metrics` - Métriques clés
- `GET /api/dashboard/charts` - Données graphiques

### Fraud
- `POST /api/fraud/detect` - Détection fraude
- `GET /api/fraud/suspicious-activities` - Activités suspectes
- `GET /api/fraud/stats` - Statistiques fraude

### Performance
- `GET /api/performance/metrics` - Métriques performance
- `GET /api/performance/api-response-times` - Temps réponse API
- `GET /api/performance/database-latency` - Latence BDD

### Search
- `GET /api/search/` - Recherche logs
- `GET /api/search/autocomplete` - Suggestions

---

## ✅ Checklist de Déploiement

- [x] Structure complète du projet
- [x] Backend Flask avec 6 routes
- [x] 9 services métier implémentés
- [x] 3 modèles de données
- [x] Configuration ELK Stack complète
- [x] Docker Compose orchestration
- [x] Tests unitaires (15+ tests)
- [x] Documentation complète (3 docs)
- [x] Scripts utilitaires (2 scripts)
- [x] Configuration MongoDB
- [x] Configuration Redis
- [x] Gestion des erreurs
- [x] Validation des données
- [x] Cache Redis
- [x] Détection de fraude
- [x] Analytics avancés
- [x] Recherche full-text
- [x] API RESTful
- [x] Health checks
- [x] Logging centralisé

---

## 🎓 Prochaines Étapes

### Développement
1. Ajouter authentification JWT
2. Implémenter notifications email
3. Créer dashboards Kibana personnalisés
4. Ajouter ML pour détection fraude
5. Implémenter rate limiting

### Infrastructure
1. Setup Kubernetes pour production
2. Configurer CI/CD pipeline
3. Ajouter monitoring Prometheus + Grafana
4. Implémenter backup automatique
5. Configurer TLS/SSL

### Tests
1. Tests d'intégration complets
2. Tests de charge (Locust/JMeter)
3. Tests de sécurité
4. Augmenter couverture à 90%+

---

## 📚 Ressources

### Documentation
- `docs/architecture.md` - Architecture détaillée
- `docs/api_documentation.md` - Documentation API complète
- `docs/quick_start.md` - Guide de démarrage
- `README.md` - Vue d'ensemble du projet

### Scripts
- `scripts/generate_sample_logs.py` - Génération de logs
- `scripts/setup_elasticsearch.py` - Setup ES

### Configuration
- `.env.example` - Variables d'environnement
- `docker-compose.yml` - Orchestration services
- `backend/config.py` - Configuration application

---

## 🏆 Résumé

✅ **Projet Big Data complet et fonctionnel**
- Architecture microservices moderne
- Stack ELK entièrement configurée
- API RESTful complète avec 20+ endpoints
- Détection de fraude intelligente
- Analytics avancés en temps réel
- Tests unitaires et documentation
- Prêt pour le déploiement

**Le projet est maintenant prêt à être utilisé et déployé ! 🚀**

---

**Date de création** : 10 Décembre 2025  
**Version** : 1.0.0  
**Statut** : ✅ Complet et Opérationnel
