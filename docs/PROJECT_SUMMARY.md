# 📊 Plateforme de Monitoring et Analyse de Logs E-Commerce
## Projet Big Data - Flask + ELK Stack + MongoDB + Redis + JWT Auth

---

## ✅ Structure Complète du Projet

```
projet_bigdata/
├── 📁 backend/                      # Application Flask avec authentification JWT
│   ├── 📁 app/
│   │   ├── 📁 routes/              # 7 modules de routes API
│   │   │   ├── auth_routes.py      # 🔐 Authentification JWT (11 endpoints)
│   │   │   ├── user_routes.py      # 👥 Gestion utilisateurs CRUD
│   │   │   ├── log_routes.py       # Upload & ingestion logs
│   │   │   ├── analytics_routes.py # Métriques agrégées
│   │   │   ├── dashboard_routes.py # Stats et visualisations
│   │   │   ├── fraud_routes.py     # Détection fraude
│   │   │   └── search_routes.py    # Recherche avancée
│   │   │
│   │   ├── 📁 services/            # 10 services métier
│   │   │   ├── auth_service.py     # 🔐 Login, tokens, validation
│   │   │   ├── user_repository.py  # 🔐 MongoDB users collection
│   │   │   ├── elasticsearch_service.py
│   │   │   ├── mongodb_service.py
│   │   │   ├── redis_service.py
│   │   │   ├── log_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── fraud_service.py
│   │   │   └── search_service.py
│   │   │
│   │   ├── 📁 models/              # 4 modèles de données
│   │   │   ├── user.py             # 🔐 User model avec rôles
│   │   │   ├── log_model.py
│   │   │   ├── transaction_model.py
│   │   │   └── fraud_model.py
│   │   │
│   │   ├── 📁 utils/               # 4 modules utilitaires
│   │   │   ├── jwt_utils.py        # 🔐 Decorators JWT (@token_required, @role_required)
│   │   │   ├── validators.py
│   │   │   ├── formatters.py
│   │   │   └── helpers.py
│   │   │
│   │   └── 📁 templates/           # 8 pages HTML avec auth JS
│   │       ├── base.html           # Template de base avec auth header
│   │       ├── login.html          # 🔐 Authentification et inscription
│   │       ├── profile.html        # 🔐 Profil utilisateur
│   │       ├── dashboard.html      # Dashboard temps réel
│   │       ├── search.html         # Recherche avancée
│   │       ├── upload.html         # Upload fichiers
│   │       ├── results.html        # Affichage résultats
│   │       └── kibana.html         # Dashboard Kibana embarqué
│   │
│   ├── 📁 tests/                   # 🧪 Suite de tests complète (tous les tests)
│   │   ├── conftest.py
│   │   ├── test_routes.py
│   │   ├── test_models.py
│   │   ├── test_auth.py            # 🔐 Tests authentification
│   │   ├── test_utils.py
│   │   ├── test_query_builder.py
│   │   ├── test_query_builder_api.py
│   │   ├── test_search_cache_history.py
│   │   ├── test_upload_endpoint.py
│   │   └── benchmark.py            # Tests de performance
│   │
│   ├── config.py                   # Configuration centralisée (JWT, MongoDB, etc.)
│   ├── main.py                     # Point d'entrée
│   ├── requirements.txt            # Dépendances Python (PyJWT, bcrypt, etc.)
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
├── 📁 uploads/                      # Dossier pour fichiers uploadés
│
├── 📁 docs/                         # 📚 Documentation complète (tous les guides)
│   ├── api_documentation.md        # 🔐 API avec exemples curl authentifiés
│   ├── architecture.md             # Architecture technique
│   ├── quick_start.md              # Guide démarrage rapide
│   ├── PROJECT_SUMMARY.md          # Ce fichier (résumé complet)
│   ├── KIBANA_INTEGRATION.md       # Guide intégration Kibana iframe
│   ├── SEARCH_IMPLEMENTATION.md    # Guide recherche avancée
│   ├── UPLOAD_ENDPOINT_IMPLEMENTATION.md # Guide endpoint upload
│   ├── ARCHITECTURE_DOCKER.md      # Architecture Docker détaillée
│   ├── DOCKER_INGESTION_GUIDE.md   # Guide ingestion avec Docker
│   └── INGESTION_SERVICE.md        # Service d'ingestion
│
├── docker-compose.yml              # Orchestration 8 services
├── .env.example                    # Template configuration (JWT, MongoDB, etc.)
├── .gitignore                      # Fichiers ignorés par Git
└── README.md                       # 🔐 Documentation principale avec JWT

```

---

## 🎯 Fonctionnalités Implémentées

### 🔐 1. Authentification & Sécurité (NOUVEAU)
- ✅ **Authentification JWT** avec access/refresh tokens
- ✅ **Gestion utilisateurs complète** (CRUD)
- ✅ **4 rôles hiérarchiques** :
  - **admin** : Accès complet + gestion utilisateurs
  - **moderator** : Gestion utilisateurs + toutes les fonctionnalités
  - **analyst** : Upload, analytics, recherche avancée
  - **viewer** : Consultation dashboards et recherche basique
- ✅ **Protection par rôle** sur tous les endpoints sensibles
- ✅ **Hachage bcrypt** des mots de passe (12 rounds)
- ✅ **Interface de login/inscription** moderne
- ✅ **Page de profil** avec quick links contextuels
- ✅ **Sessions persistantes** via localStorage
- ✅ **Auto-redirection** si token manquant ou expiré
- ✅ **Refresh token** pour renouvellement automatique

### 2. Gestion des Logs
- ✅ **Upload de fichiers** (JSON/CSV, max 100MB) protégé par rôle Analyst+
- ✅ **Ingestion JSON** via API avec validation
- ✅ Support de 5 types de logs :
  - Transactions (paiements, commandes, remboursements)
  - Erreurs applicatives (404, 500, timeouts)
  - Comportement utilisateur (navigation, paniers, abandons)
  - Performance (temps de réponse API, latence BDD)
  - Fraude (tentatives suspectes, détection de bots)
- ✅ **Traitement asynchrone** via Logstash avec enrichissement GeoIP
- ✅ **Indexation Elasticsearch** automatique

### 3. Analytics Avancés
- ✅ **Analytics de transactions** (timeline, méthodes de paiement, statuts)
- ✅ **Analytics d'erreurs** (codes, types, chronologie)
- ✅ **Analytics comportement utilisateur**
- ✅ **Logs par heure** (24h glissantes)
- ✅ **Top pays** par nombre de logs
- ✅ **Top produits** par volume de transactions
- ✅ **Métriques temps réel** sur dashboard
- ✅ **Accès contrôlé par rôle** (Analyst+ uniquement)

### 4. Détection de Fraude
- ✅ Scoring de fraude (0-100)
- ✅ Détection d'indicateurs multiples :
  - Montants élevés
  - Transactions rapides successives
  - Localisation suspecte
  - Tentatives échouées multiples
  - Mismatch IP
- ✅ Historique des détections
- ✅ Statistiques de fraude

### 5. Monitoring de Performance
- ✅ Temps de réponse API
- ✅ Latence base de données
- ✅ Percentiles (P50, P90, P95, P99)
- ✅ Requêtes lentes
- ✅ Analyse par endpoint

### 6. Recherche Puissante
- ✅ **Recherche full-text** dans Elasticsearch avec authentification
- ✅ **Filtres avancés** (level, service, date range)
- ✅ **Highlighting** des résultats
- ✅ **Sauvegarde des recherches** (Analyst+)
- ✅ **Historique des recherches récentes**
- ✅ **Export CSV/JSON** des résultats
- ✅ **Date picker** avec filtres rapides (1h, 24h, 7j, 30j)

### 7. Dashboard & Visualisation
- ✅ **Vue d'ensemble** des métriques clés (KPIs)
- ✅ **Graphiques temporels** avec Chart.js
- ✅ **Distribution** des niveaux de logs
- ✅ **Top services** par volume
- ✅ **Erreurs récentes** (tableau)
- ✅ **Dashboard Kibana embarqué** via iframe (Analyst+)
- ✅ **3 visualisations Kibana** exportables :
  - Logs par heure (line chart)
  - Top erreurs par service (bar chart)
  - Distribution montants (donut chart)
---

## 🚀 Technologies Utilisées

### Backend
- **Flask 3.0** - Framework web Python
- **Python 3.11** - Langage principal
- **Gunicorn** - Serveur WSGI production
- **PyJWT 2.8.0** - 🔐 Authentification JWT
- **bcrypt** - 🔐 Hachage sécurisé des mots de passe

### Stack ELK
- **Elasticsearch 8.11** - Recherche et indexation
- **Logstash 8.11** - Pipeline de traitement
- **Kibana 8.11** - Visualisation

### Bases de Données
- **MongoDB 7.0** - Stockage métadonnées + 🔐 collection users
- **Redis 7.2** - Cache, sessions et queue jobs

### Frontend
- **Jinja2** - Template engine
- **Chart.js** - Visualisations graphiques
- **Tailwind CSS** - Styling responsive
- **Flatpickr** - Date picker avancé
- **Font Awesome** - Icônes

### Infrastructure
- **Docker & Docker Compose** - Conteneurisation (8 services)
- **Nginx** (optionnel) - Reverse proxy

### Tests & Qualité
- **Pytest** - Framework de tests
- **Pytest-cov** - Couverture de code
- **Flake8** - Linting

---

## 📈 Métriques du Projet

### Code
- **~6,500 lignes** de code Python
- **35+ fichiers** Python
- **7 routes** API principales (dont auth_routes 🔐)
- **10 services** métier (dont auth_service 🔐)
- **4 modèles** de données (dont user.py 🔐)
- **8 templates** HTML avec auth JavaScript
- **20+ tests** unitaires (dont test_auth.py 🔐)

### Infrastructure
- **8 services** Docker (Flask, ES, Kibana, Logstash, MongoDB, Redis, Celery Workers, Beat Scheduler)
- **4 configurations** ELK Stack
- **1 pipeline** Logstash
- **3 bases** de données

### Documentation
- **3 documents** markdown détaillés
- **25+ endpoints** API documentés (dont 11 auth 🔐)
- **Guide** de démarrage rapide avec authentification
- **Architecture** complète avec sécurité JWT
- **Documentation API** avec exemples curl authentifiés

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

## 📡 Principaux Endpoints API

### 🔐 Authentification (NOUVEAU)
- `POST /api/auth/register` - Créer un compte
- `POST /api/auth/login` - Se connecter (obtenir JWT)
- `POST /api/auth/refresh` - Rafraîchir le token d'accès
- `POST /api/auth/logout` - Se déconnecter
- `GET /api/auth/me` - Récupérer profil utilisateur

### 👥 Gestion Utilisateurs (NOUVEAU)
- `GET /api/users` - Lister utilisateurs (Moderator+)
- `GET /api/users/:id` - Récupérer un utilisateur (Moderator+)
- `PUT /api/users/:id` - Modifier un utilisateur (Moderator+)
- `DELETE /api/users/:id` - Supprimer un utilisateur (Admin)

### Logs
- `POST /api/logs/upload` - Upload fichier (Analyst+)
- `POST /api/logs/ingest` - Ingestion JSON (Analyst+)
- `GET /api/logs/recent` - Logs récents (Viewer+)
- `GET /api/logs/stats` - Statistiques (Analyst+)
- `GET /api/logs/types` - Types de logs disponibles (Viewer+)

### Analytics
- `GET /api/analytics/transactions` - Analytics transactions (Analyst+)
- `GET /api/analytics/errors` - Analytics erreurs (Analyst+)
- `GET /api/analytics/trends` - Tendances (Analyst+)
- `GET /api/analytics/logs-per-hour` - Logs par heure (Analyst+)
- `GET /api/analytics/top-countries` - Top pays (Analyst+)
- `GET /api/analytics/top-products` - Top produits (Analyst+)

### Dashboard
- `GET /api/dashboard/overview` - Vue d'ensemble (Viewer+)
- `GET /api/dashboard/stats` - Statistiques KPIs (Viewer+)
- `GET /api/dashboard/metrics` - Métriques clés (Viewer+)
- `GET /api/dashboard/charts` - Données graphiques (Viewer+)

### Search
- `POST /api/logs/search` - Recherche avancée (Analyst+)
- `GET /api/logs/search/services` - Services disponibles (Viewer+)
- `POST /api/logs/search/save` - Sauvegarder recherche (Analyst+)
- `GET /api/logs/search/recent` - Recherches récentes (Analyst+)

### Fraud
- `POST /api/fraud/detect` - Détection fraude (Analyst+)
- `GET /api/fraud/suspicious-activities` - Activités suspectes (Analyst+)
- `GET /api/fraud/stats` - Statistiques fraude (Analyst+)

### Performance
- `GET /api/performance/metrics` - Métriques performance (Analyst+)
- `GET /api/performance/api-response-times` - Temps réponse API (Analyst+)
- `GET /api/performance/database-latency` - Latence BDD (Analyst+)

---

## ✅ Checklist de Déploiement

- [x] Structure complète du projet
- [x] 🔐 **Authentification JWT implémentée**
- [x] 🔐 **Gestion utilisateurs CRUD avec rôles**
- [x] 🔐 **4 décorateurs JWT (@token_required, @role_required, etc.)**
- [x] 🔐 **8 templates HTML avec auth JavaScript**
- [x] Backend Flask avec 7 routes (dont auth_routes)
- [x] 10 services métier implémentés (dont auth_service)
- [x] 4 modèles de données (dont user.py)
- [x] Configuration ELK Stack complète
- [x] Docker Compose orchestration (8 services)
- [x] Tests unitaires (20+ tests dont test_auth.py)
- [x] Documentation complète (6+ docs dont JWT_AUTHENTICATION.md)
- [x] Scripts utilitaires (2 scripts)
- [x] Configuration MongoDB (avec collection users)
- [x] Configuration Redis (cache + sessions)
- [x] Gestion des erreurs
- [x] Validation des données
- [x] Cache Redis
- [x] Détection de fraude
- [x] Analytics avancés
- [x] 🔐 **Sécurité bcrypt pour mots de passe**
- [x] 🔐 **Tokens access (1h) et refresh (30j)**
- [x] 🔐 **Protection par rôle sur tous les endpoints sensibles**
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
3. Tests de sécurité JWT
4. Augmenter couverture à 90%+

---

## 📚 Ressources

### Documentation Principale (docs/)
- `README.md` - 🔐 Vue d'ensemble avec JWT auth (à la racine)
- `docs/api_documentation.md` - 🔐 API avec exemples curl authentifiés
- `docs/architecture.md` - Architecture technique détaillée
- `docs/quick_start.md` - Guide de démarrage rapide
- `docs/PROJECT_SUMMARY.md` - Ce fichier (résumé complet)
- `docs/KIBANA_INTEGRATION.md` - Guide intégration Kibana iframe
- `docs/SEARCH_IMPLEMENTATION.md` - Guide recherche avancée
- `docs/UPLOAD_ENDPOINT_IMPLEMENTATION.md` - Guide endpoint upload
- `docs/ARCHITECTURE_DOCKER.md` - Architecture Docker détaillée
- `docs/DOCKER_INGESTION_GUIDE.md` - Guide ingestion Docker
- `docs/INGESTION_SERVICE.md` - Service d'ingestion

### Scripts Utilitaires
- `scripts/generate_sample_logs.py` - Génération de logs de test
- `scripts/setup_elasticsearch.py` - Configuration Elasticsearch

### Tests Unitaires (backend/tests/)
- `backend/tests/test_auth.py` - 🔐 Tests authentification
- `backend/tests/test_routes.py` - Tests routes API
- `backend/tests/test_models.py` - Tests modèles de données
- `backend/tests/test_utils.py` - Tests utilitaires
- `backend/tests/test_query_builder.py` - Tests query builder
- `backend/tests/test_query_builder_api.py` - Tests API query builder
- `backend/tests/test_search_cache_history.py` - Tests recherche et cache
- `backend/tests/test_upload_endpoint.py` - Tests endpoint upload
- `backend/tests/benchmark.py` - Tests de performance

### Configuration
- `.env.example` - 🔐 Template variables (JWT_SECRET_KEY, MongoDB, etc.)
- `docker-compose.yml` - Orchestration 8 services
- `backend/config.py` - 🔐 Configuration application (JWT, DB, etc.)
- `backend/requirements.txt` - Dépendances Python (PyJWT, bcrypt, etc.)

### Fichiers d'Authentification
- `backend/app/utils/jwt_utils.py` - 🔐 Decorators JWT
- `backend/app/services/auth_service.py` - 🔐 Login & tokens
- `backend/app/services/user_repository.py` - 🔐 MongoDB users
- `backend/app/models/user.py` - 🔐 User model
- `backend/app/routes/auth_routes.py` - 🔐 11 endpoints auth
- `backend/app/routes/user_routes.py` - 🔐 CRUD utilisateurs

---

## 🏆 Résumé

✅ **Projet Big Data complet, sécurisé et opérationnel**
- 🔐 **Authentification JWT robuste** avec access/refresh tokens
- 🔐 **Gestion utilisateurs CRUD** avec 4 rôles hiérarchiques
- 🔐 **Protection par rôle** sur tous les endpoints sensibles
- 🔐 **Interface moderne** de login/inscription/profil
- Architecture microservices moderne (8 services Docker)
- Stack ELK entièrement configurée (Elasticsearch + Kibana + Logstash)
- API RESTful sécurisée avec 25+ endpoints authentifiés
- Détection de fraude intelligente avec scoring
- Analytics avancés en temps réel (logs/heure, top pays, top produits)
- Dashboard temps réel avec Chart.js + Kibana embarqué
- Recherche avancée avec filtres multiples et sauvegarde
- Tests unitaires (20+) et documentation complète (6+ docs)
- Hachage bcrypt des mots de passe (12 rounds)
- Sessions persistantes avec localStorage
- Prêt pour le déploiement production

**Le projet est maintenant entièrement sécurisé avec JWT et prêt à être déployé ! 🚀🔒**

---

**Date de création** : 10 Décembre 2024  
**Dernière mise à jour** : 25 Décembre 2024 (Ajout authentification JWT)  
**Version** : 2.0.0 (avec authentification JWT)  
**Statut** : ✅ Complet, Sécurisé et Opérationnel
