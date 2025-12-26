# 🚀 Plateforme BigData - Analyse de Logs E-Commerce

Plateforme complète de centralisation, indexation et visualisation de logs e-commerce avec upload API, traitement automatique et dashboards temps réel.

## 🏗️ Stack Technologique

| Composant | Technologie | Port |
|-----------|-------------|------|
| **Backend API** | Flask 3.0 + Gunicorn | 5001 |
| **Frontend** | Jinja2 + Chart.js + Tailwind CSS | - |
| **Recherche** | Elasticsearch 8.11 | 9200 |
| **Visualisation** | Kibana 8.11 | 5601 |
| **Traitement** | Logstash 8.11 | 5000 |
| **Base de données** | MongoDB 7.0 | 27017 |
| **Cache/Queue** | Redis 7.2 | 6379 |

### Architecture de Flux

```
┌─────────────┐     POST /upload      ┌──────────────┐
│  Client     │─────────────────────►│  Flask API   │
│  (HTTP)     │◄─────────────────────│  (5001)      │
└─────────────┘   JSON Response       └──────┬───────┘
                                             │
                  ┌──────────────────────────┤
                  │                          │
                  ▼                          ▼
          ┌───────────────┐         ┌───────────────┐
          │   MongoDB     │         │     Redis     │
          │   (Metadata)  │         │    (Queue)    │
          │  - job_id     │         │ ingest_jobs   │
          │  - status     │         └───────┬───────┘
          │  - preview    │                 │
          └───────┬───────┘                 │ lpop
                  │                         ▼
                  │               ┌──────────────────┐
                  │               │ Ingestion Service│
                  │               │  - Listen queue  │
                  │               │  - Move files    │
                  │◄──────────────┤  - Update status │
                  │ Update status └────────┬─────────┘
                  │                        │ Copy file
                  │                        ▼
                  │               ┌──────────────────┐
                  │               │    Logstash      │
                  │               │  - Watch /uploads│
                  │               │  - Parse JSON/CSV│
                  │               │  - GeoIP enrich  │
                  │               └────────┬─────────┘
                  │                        │ Bulk index
                  │                        ▼
                  │               ┌──────────────────┐
                  │               │  Elasticsearch   │
                  │               │  logs-ecom-*     │
                  │               │  36+ documents   │
                  │               └──────────────────┘
                  │                        │
                  │                        ▼
                  └───────────────►│     Kibana       │
                                  │  Visualization   │
                                  └──────────────────┘
```

---

## 🚀 Installation

### Prérequis
```powershell
# Windows 10/11 avec WSL2
# Docker Desktop (min 8 GB RAM alloués)
# Python 3.11+
```

### Démarrage Rapide
```powershell
# 1. Cloner le projet
cd c:\projet_bigdata

# 2. Configurer l'environnement
Copy-Item .env.example .env
# Éditer .env pour changer les mots de passe (production)

# 3. Démarrer tous les services (8 containers)
docker-compose up -d

# 4. Vérifier le statut (~60s pour health checks)
docker-compose ps

# Résultat attendu : 8 services "Up" et "healthy"
```

### Services Disponibles

| Service | URL | Description |
|---------|-----|-------------|
| Flask API | http://localhost:5001 | REST API + Health check |
| Elasticsearch | http://localhost:9200 | Recherche & indexation |
| Kibana | http://localhost:5601 | Dashboards & visualisation |
| MongoDB | localhost:27017 | Métadonnées & statuts |
| Redis | localhost:6379 | Queue & cache |

---

## 📊 Benchmark & Tests Validés

### Tests Automatiques (Tous ✅)

```powershell
# Exécuter tous les tests
python test_upload_endpoint.py

# Résultats:
# ✅ Upload JSON (12 lignes) - 201 Created
# ✅ Upload CSV (12 lignes) - 201 Created
# ✅ Rejet fichier .txt - 400 Bad Request
# ✅ Rejet fichier vide - 400 Bad Request
# ✅ Rejet sans fichier - 400 Bad Request
```

### Benchmark de Performance

```powershell
# Exécuter le benchmark complet
python benchmark.py
```

**Résultats Mesurés** :

| Métrique | Valeur | Status |
|----------|--------|--------|
| **Latence services** | 51.83ms avg | ✅ Excellent |
| **Throughput upload** | 189.41 KB/s | ✅ Bon |
| **Upload petit (10 lignes)** | 0.77s | ✅ |
| **Upload moyen (100 lignes)** | 0.93s | ✅ |
| **Upload large (1000 lignes)** | 0.49s | ✅ |
| **Documents indexés** | 36+ | ✅ |
| **Indices actifs** | 2 (par date) | ✅ |

### Capacités Testées

| Fonctionnalité | Capacité | Testé |
|----------------|----------|-------|
| **Taille max fichier** | 100 MB | ✅ |
| **Formats supportés** | CSV, JSON | ✅ |
| **Validation fichier** | Extension, taille, contenu | ✅ |
| **Preview extraction** | 10 premières lignes | ✅ |
| **MongoDB tracking** | job_id, status, timestamps | ✅ |
| **Redis queue** | FIFO async processing | ✅ |
| **Auto-retry** | 3 tentatives, 5s delay | ✅ |
| **GeoIP enrichment** | IP → Geo coordinates | ✅ |
| **Error handling** | DLQ + fallback index | ✅ |
| **Status updates** | pending → processing → completed | ✅ |
| **Query Builder ES** | Filtres multiples + sanitization | ✅ **NEW!** |
| **Recherche avancée** | 10+ paramètres combinables | ✅ **NEW!** |
| **Cache Redis** | TTL 60s pour performances | ✅ **NEW!** |
| **Historique MongoDB** | search_history collection | ✅ **NEW!** |
| **Pagination** | Page 1-∞, size 1-1000 | ✅ **NEW!** |
| **Sécurité inputs** | XSS, injection, validation | ✅ **NEW!** |

---

## 🛠️ API Endpoints

### Upload de Fichiers

#### POST /api/logs/upload
Upload un fichier CSV ou JSON avec validation, preview, et queuing automatique.

**Request** :
```bash
curl -X POST http://localhost:5001/api/logs/upload \
  -F "file=@logs.json"
```

**Response (201 Created)** :
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "file_id": "694d2f0baaee036c497259a6",
    "job_id": "7ec5e928-2042-488c-a578-7f9936d32b47",
    "filename": "logs.json",
    "file_type": "json",
    "file_size": 1465,
    "total_lines": 12,
    "preview_lines": 10,
    "preview": [
      {
        "timestamp": "2025-12-25T10:00:00Z",
        "log_type": "transaction",
        "user_id": "USER123",
        "amount": 99.99,
        "ip": "8.8.8.8"
      }
    ],
    "uploaded_at": "2025-12-25T12:33:15.588643"
  }
}
```

**Validations** :
- ✅ Extension : `.csv` ou `.json` uniquement
- ✅ Taille : Max 100 MB
- ✅ Contenu : Parsing JSON/CSV validé
- ✅ Nom fichier : Sécurisé (secure_filename)

**Erreurs possibles** :
```json
// 400 - Extension invalide
{"success": false, "error": "File extension '.txt' not allowed"}

// 400 - Fichier vide
{"success": false, "error": "File is empty"}

// 400 - Taille dépassée
{"success": false, "error": "File size exceeds 100 MB limit"}
```

---

### Dashboard Web (Frontend)

#### GET /dashboard
Interface web interactive avec visualisation temps réel des KPIs et analytics.

**🎨 Fonctionnalités** :
- ✅ **KPI Cards** : Total logs, erreurs, utilisateurs uniques, temps de réponse moyen
- ✅ **Chart.js Timeline** : Logs par heure (24h) avec distinction erreurs/total
- ✅ **Distribution Niveaux** : Graphique Doughnut (INFO, WARNING, ERROR, CRITICAL)
- ✅ **Top Services** : Classement des services par volume de logs
- ✅ **Erreurs Récentes** : Tableau des 10 dernières erreurs avec détails
- ✅ **Bouton Kibana** : Lien direct vers dashboard Kibana avancé
- ✅ **Auto-refresh** : Actualisation automatique toutes les 30 secondes
- ✅ **Responsive** : Design Tailwind CSS adaptatif mobile/desktop
- ✅ **Health Status** : Indicateurs temps réel Elasticsearch, Redis, MongoDB

**Query Parameters** :

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `range` | string | Plage temporelle | `24h`, `7d`, `30d` (défaut: `24h`) |

**Exemples d'utilisation** :

```bash
# Dashboard 24 heures (défaut)
http://localhost:5001/dashboard

# Dashboard 7 jours
http://localhost:5001/dashboard?range=7d

# Dashboard 30 jours
http://localhost:5001/dashboard?range=30d
```

**API Endpoints Associés** :

```bash
# GET /api/dashboard/kpis - KPIs JSON pour refresh AJAX
curl "http://localhost:5001/api/dashboard/kpis?range=24h"

# GET /api/dashboard/health - Health check systèmes
curl "http://localhost:5001/api/dashboard/health"

# GET /api/dashboard/view - Vue HTML alternative
curl "http://localhost:5001/api/dashboard/view"
```

**Réponse KPIs (JSON)** :
```json
{
  "total_logs": 15234,
  "total_errors": 234,
  "unique_users": 1523,
  "avg_response_time": 125,
  "logs_growth": 12.5,
  "error_rate": 1.54,
  "active_users": 45,
  "logs_per_hour": [
    {"hour": "10:00", "total": 650, "errors": 12},
    {"hour": "11:00", "total": 720, "errors": 8}
  ],
  "log_levels_distribution": {
    "INFO": 12500,
    "WARNING": 2000,
    "ERROR": 200,
    "CRITICAL": 34
  },
  "top_services": [
    {"name": "payment-service", "count": 5200, "percentage": 34.1},
    {"name": "order-service", "count": 4100, "percentage": 26.9}
  ],
  "recent_errors": [
    {
      "timestamp": "2025-12-25 12:45:30",
      "service": "payment-service",
      "message": "Database connection timeout",
      "level": "ERROR"
    }
  ],
  "last_update": "2025-12-25 12:45:35"
}
```

**Health Status** :
```json
{
  "success": true,
  "health": {
    "elasticsearch": "Connecté",
    "redis": "Actif",
    "mongodb": "Connecté"
  }
}
```

**Caractéristiques Techniques** :
- **Cache** : Les KPIs sont cachés Redis pendant 60 secondes
- **Visualisation** : Chart.js 4.4.0 pour graphiques interactifs
- **Style** : Tailwind CSS avec thème gradient purple
- **Icons** : Font Awesome 6.5.1
- **Responsive** : Grid adaptatif (mobile → desktop)
- **Performance** : Lazy loading des graphiques, pagination backend

---

### Recherche Elasticsearch (Query Builder)

#### GET /api/search
Recherche avancée avec Query Builder Elasticsearch - supporte filtres multiples, pagination, tri, sanitization complète, **cache Redis (TTL 60s)**, et **historique MongoDB**.

**🚀 Fonctionnalités** :
- ✅ **Query Builder DSL** : Construction sécurisée de queries ES
- ✅ **Cache Redis** : TTL 60 secondes pour réduire la charge ES
- ✅ **Historique MongoDB** : Sauvegarde automatique des recherches (collection `search_history`)
- ✅ **Pagination avancée** : Pages 1-∞, size 1-1000
- ✅ **Multi-filtres** : 10+ paramètres combinables
- ✅ **Sanitization** : Protection contre SQL injection, XSS, inputs malveillants

**Query Parameters** :

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `q` | string | Recherche texte libre (multi-champs) | `error timeout` |
| `level` | string | Niveau de log | `ERROR`, `WARNING`, `INFO` |
| `service` | string | Nom du service | `payment`, `checkout` |
| `log_type` | string | Type de log | `transaction`, `error`, `fraud` |
| `date_from` | string | Date début (ISO 8601) | `2025-12-01` ou `2025-12-01T10:00:00` |
| `date_to` | string | Date fin (ISO 8601) | `2025-12-31` |
| `user_id` | string | ID utilisateur | `USER123` |
| `min_amount` | float | Montant minimum | `100.00` |
| `max_amount` | float | Montant maximum | `1000.00` |
| `page` | int | Numéro de page (1-indexed) | `2` |
| `size` | int | Résultats par page (max 1000) | `50` |
| `sort_field` | string | Champ de tri | `@timestamp`, `amount` |
| `sort_order` | string | Ordre de tri | `asc`, `desc` |

**Exemples d'utilisation** :

```bash
# 1. Recherche simple
GET /api/search?q=timeout

# 2. Filtrer par niveau ERROR
GET /api/search?level=ERROR&size=50

# 3. Logs du service payment en décembre
GET /api/search?service=payment&date_from=2025-12-01&date_to=2025-12-31

# 4. Recherche combinée avec pagination
GET /api/search?q=timeout&level=ERROR&service=payment&page=2&size=20

# 5. Transactions par montant
GET /api/search?log_type=transaction&min_amount=100&max_amount=1000&sort_field=amount&sort_order=desc

# 6. Logs d'un utilisateur spécifique
GET /api/search?user_id=USER123&date_from=2025-12-20

# 7. Fraudes détectées
GET /api/search?log_type=fraud&sort_field=@timestamp&sort_order=desc
```

**Response (200 OK)** :
```json
{
  "success": true,
  "data": {
    "total": 156,
    "page": 1,
    "page_size": 20,
    "total_pages": 8,
    "cached": false,
    "results": [
      {
        "id": "abc123",
        "score": 4.5,
        "source": {
          "@timestamp": "2025-12-25T10:30:00Z",
          "level": "ERROR",
          "service": "payment",
          "message": "Payment timeout after 30s",
          "user_id": "USER456",
          "amount": 99.99
        },
        "highlight": {
          "message": ["Payment <mark>timeout</mark> after 30s"]
        }
      }
    ],
    "query": "timeout",
    "filters": {
      "level": "ERROR",
      "service": "payment",
      "start_date": "2025-12-01",
      "end_date": "2025-12-31"
    },
    "sort": {
      "field": "@timestamp",
      "order": "desc"
    }
  }
}
```

**⚡ Cache & Performance** :
- **Cache Redis** : TTL 60 secondes basé sur hash des paramètres
- **Cache HIT** : `cached: true` dans la réponse
- **Cache MISS** : Query exécutée sur ES, résultats mis en cache
- **Cache key** : `search:<md5_hash_params>` (garantit unicité)
- **Invalidation** : Automatique après 60s

**📊 Historique des Recherches (MongoDB)** :
```javascript
// Collection: search_history
{
  "timestamp": ISODate("2025-12-25T10:30:00Z"),
  "query": "timeout",
  "filters": {
    "log_type": "error",
    "level": "ERROR",
    "service": "payment",
    "start_date": "2025-12-01",
    "end_date": "2025-12-31"
  },
  "pagination": {
    "page": 1,
    "size": 20
  },
  "results_count": 156,
  "user_ip": "192.168.1.100"
}
```

**Utilité de l'historique** :
- 📈 Analyser les patterns de recherche utilisateurs
- 🔍 Identifier les requêtes fréquentes (optimisation cache)
- 🐛 Debug : comprendre les recherches qui échouent
- 📊 Métriques : top queries, services les plus recherchés

**Sécurité & Sanitization** :
- ✅ **Injection SQL** : Paramètres sanitisés et validés
- ✅ **XSS** : Caractères spéciaux échappés
- ✅ **Texte limité** : Max 500 caractères pour free text
- ✅ **Validation dates** : Formats ISO 8601 uniquement
- ✅ **Pagination bornée** : Size max 1000, page min 1
- ✅ **Niveaux validés** : Liste whitelist (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ **Fallbacks sûrs** : Valeurs par défaut si invalides

**Tests disponibles** :
```powershell
# Tester l'API de recherche
python test_query_builder_api.py

# Tests incluent:
# - Recherche basique
# - Filtres combinés
# - Pagination
# - Tri personnalisé
# - Sécurité (injection, XSS)
# - Edge cases (unicode, texte long)
```

---

## 📁 Structure du Projet (Nettoyée)

```
projet_bigdata/
│
├── backend/                           # Application Flask
│   ├── app/
│   │   ├── routes/
│   │   │   ├── logs_routes.py         # ✅ POST /upload endpoint
│   │   │   ├── dashboard_routes.py    # ✅ GET /dashboard + API KPIs
│   │   │   ├── search_routes.py       # ✅ GET /search (Query Builder)
│   │   │   ├── analytics_routes.py    # Agrégations
│   │   │   └── fraud_routes.py        # Détection fraude
│   │   ├── services/
│   │   │   ├── log_service.py         # ✅ Upload logic + preview
│   │   │   ├── dashboard_service.py   # ✅ KPIs et metrics
│   │   │   ├── search_service.py      # ✅ Search avec Query Builder
│   │   │   ├── redis_service.py       # ✅ Queue + cache methods
│   │   │   ├── mongodb_service.py     # ✅ Metadata CRUD
│   │   │   ├── elasticsearch_service.py
│   │   │   └── analytics_service.py
│   │   ├── utils/
│   │   │   ├── validators.py          # ✅ File validation
│   │   │   ├── query_builder.py       # ✅ ES Query Builder
│   │   │   ├── helpers.py
│   │   │   └── formatters.py
│   │   ├── templates/
│   │   │   └── dashboard.html         # ✅ Dashboard web UI
│   │   ├── static/
│   │   │   ├── css/                   # Styles personnalisés
│   │   │   └── js/                    # Scripts JS
│   │   ├── models/                    # MongoDB schemas
│   │   └── celery_app.py              # Celery config
│   │
│   ├── ingestion_service.py           # ✅ Ingestion (Docker)
│   ├── main.py                        # Flask entry point
│   ├── config.py                      # Configuration
│   └── requirements.txt               # Dependencies
│
├── infra/                             # Infrastructure
│   ├── logstash/pipelines/
│   │   ├── pipeline_json.conf         # ✅ JSON pipeline
│   │   └── pipeline_csv.conf          # ✅ CSV pipeline
│   ├── elasticsearch/config/
│   └── kibana/config/
│
├── uploads/                           # ✅ Fichiers uploadés
├── docs/                              # Documentation
├── scripts/                           # Scripts utilitaires
│
├── docker-compose.yml                 # ✅ 8 services
├── Dockerfile.ingestion               # ✅ Image ingestion
├── .env                               # Configuration
│
├── test_upload_endpoint.py            # ✅ Tests upload API
├── test_query_builder_api.py          # ✅ Tests Query Builder
├── test_search_cache_history.py       # ✅ Tests cache/historique
├── benchmark.py                       # ✅ Benchmark
│
└── README.md                          # ⭐ Ce fichier

---

## 🎨 Dashboard Web - Détails Techniques

### Architecture Frontend

**Templates** : `backend/app/templates/dashboard.html`  
**Style** : Tailwind CSS 3.x (CDN)  
**Charts** : Chart.js 4.4.0  
**Icons** : Font Awesome 6.5.1

### Composants Dashboard

#### 1. **KPI Cards** (4 cartes)
- **Total Logs** : Count total avec croissance % depuis hier
- **Erreurs** : Count ERROR + CRITICAL avec taux d'erreur %
- **Utilisateurs Uniques** : Cardinality `user_id.keyword` + actifs maintenant
- **Temps Moyen** : Avg `response_time` en ms avec amélioration %

#### 2. **Charts Interactifs**
- **Timeline (Line Chart)** : Logs par heure (24h) - 2 datasets (total + erreurs)
- **Distribution (Doughnut)** : Log levels (INFO, WARNING, ERROR, CRITICAL, DEBUG)

#### 3. **Tables & Lists**
- **Top Services** : Top 5 services avec barre de progression
- **Erreurs Récentes** : 10 dernières erreurs avec timestamp, service, message, niveau

#### 4. **Action Buttons**
- **Kibana Dashboard** : Lien externe vers visualisations avancées
- **Rechercher Logs** : Redirection vers Query Builder `/api/search`
- **Upload Logs** : Modal upload (placeholder future feature)

#### 5. **Footer Health Status**
- Indicateurs temps réel : Elasticsearch (vert), Redis (rouge), MongoDB (vert)
- Status récupéré via `/api/dashboard/health`

### Endpoints Backend

| Route | Method | Description |
|-------|--------|-------------|
| `/dashboard` | GET | Render HTML template avec données initiales |
| `/api/dashboard/view` | GET | Alternative URL (même résultat) |
| `/api/dashboard/kpis` | GET | JSON KPIs pour refresh AJAX |
| `/api/dashboard/health` | GET | JSON health status systèmes |

### Cache Strategy

- **TTL** : 60 secondes (1 minute)
- **Cache Key** : `dashboard:kpis:{time_range}`
- **Invalidation** : Automatique après expiration
- **Fallback** : Données vides si erreur ES

### JavaScript Functions

```javascript
// Auto-refresh toutes les 30 secondes
startAutoRefresh() → setInterval(refreshData, 30000)

// Refresh manuel
refreshData() → fetch('/api/dashboard/kpis') → update DOM

// Change time range
updateTimeRange(range) → fetch with new range → update charts

// Show upload modal (placeholder)
showUploadModal() → alert notification
```

### Responsive Design

- **Mobile** : Grid 1 colonne, KPIs stack vertical
- **Tablet** : Grid 2 colonnes, charts responsive
- **Desktop** : Grid 4 colonnes pour KPIs, 2-3 colonnes pour content

### Performance

- **Cache Hit** : ~10ms response time
- **Cache Miss** : ~50-150ms (selon volume ES)
- **Chart Rendering** : ~50ms (client-side)
- **Total Page Load** : <500ms (first load), <100ms (cached)

---

## ⚙️ Configuration

### Variables d'Environnement (.env)

```bash
# Flask
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_SECRET_KEY=your-super-secret-key-change-in-production

# Elasticsearch
ELASTICSEARCH_HOST=elasticsearch        # Hostname Docker
ELASTICSEARCH_PORT=9200

# MongoDB
MONGODB_HOST=mongodb                    # Hostname Docker
MONGODB_PORT=27017
MONGO_USERNAME=admin
MONGO_PASSWORD=changeme                 # ⚠️ Changer en production
MONGODB_URI=mongodb://admin:changeme@mongodb:27017/ecommerce_logs?authSource=admin

# Redis
REDIS_HOST=redis                        # Hostname Docker
REDIS_PORT=6379
REDIS_PASSWORD=changeme                 # ⚠️ Changer en production

# Celery
CELERY_BROKER_URL=redis://:changeme@redis:6379/0
CELERY_RESULT_BACKEND=redis://:changeme@redis:6379/1

# Upload Configuration
MAX_FILE_SIZE_MB=100
ALLOWED_EXTENSIONS=csv,json
UPLOAD_FOLDER=/app/uploads
```

> **Architecture** : Tous les services utilisent les **hostnames Docker** (`redis`, `mongodb`) pour communiquer via le réseau interne `elk-network`.

---

## 🔄 Workflow Complet

### 1. Upload via API
```powershell
# Créer fichier test
@"
{"timestamp":"2025-12-25T14:00:00Z","log_type":"transaction","user_id":"USER999","amount":199.99}
"@ | Out-File -FilePath test.json -Encoding utf8

# Upload
curl -X POST http://localhost:5001/api/logs/upload -F "file=@test.json"
```

### 2. Traitement Automatique

```
1. Flask API
   ├─ Valide fichier (extension, taille, contenu)
   ├─ Génère job_id (UUID)
   ├─ Sauvegarde uploads/YYYYMMDD_HHMMSS_uuid_filename.json
   ├─ Extrait preview (10 lignes)
   ├─ Insère métadonnées MongoDB
   └─ Push job Redis queue

2. Ingestion Service (daemon)
   ├─ Écoute Redis queue (5s polling)
   ├─ Récupère job_id
   ├─ Update status → "processing"
   ├─ Fichier déjà dans /uploads
   └─ Update status → "completed"

3. Logstash
   ├─ Détecte fichier /uploads/*.json
   ├─ Parse JSON + GeoIP
   ├─ Bulk index Elasticsearch
   └─ Index: logs-ecom-YYYY.MM.DD

4. Elasticsearch
   ├─ Stocke documents enrichis
   └─ Disponible dans Kibana
```

### 3. Monitoring

```powershell
# Logs ingestion service
docker-compose logs -f ingestion-service

# Queue Redis
docker exec redis redis-cli -a changeme LLEN ingest_jobs

# MongoDB uploads
docker exec mongodb mongosh -u admin -p changeme --authenticationDatabase admin ecommerce_logs --quiet --eval "db.uploads.find().count()"

# Elasticsearch documents
Invoke-RestMethod -Uri "http://localhost:9200/logs-ecom-*/_count"
```

---

## 📊 Service d'Ingestion (Dockerisé)

### Caractéristiques

| Aspect | Détail |
|--------|--------|
| **Type** | Daemon Python container dédié |
| **Démarrage** | Auto avec `docker-compose up -d` |
| **Polling** | 5 secondes |
| **Retry** | 3 tentatives, 5s delay |
| **Logging** | Stdout + fichier |

### Commandes

```powershell
# Logs temps réel
docker-compose logs -f ingestion-service

# Redémarrer
docker-compose restart ingestion-service

# Statistiques
docker stats ingestion-service
```

---

## 🔍 Troubleshooting

### Health Checks
```powershell
# Tous les services
docker-compose ps

# API Health
Invoke-RestMethod -Uri "http://localhost:5001/api/health"

# Elasticsearch
Invoke-RestMethod -Uri "http://localhost:9200/_cluster/health"
```

### Problèmes Communs

**Service unhealthy** :
```powershell
docker-compose logs <service_name>
docker-compose restart <service_name>
```

**Upload fonctionne mais pas d'indexation ES** :
```powershell
# Vérifier Logstash traite fichiers
docker-compose logs logstash | Select-String "processed"

# Forcer retraitement
docker exec logstash rm -f /usr/share/logstash/data/plugins/inputs/file/.sincedb*
docker-compose restart logstash
```

**Queue Redis bloquée** :
```powershell
# Vérifier taille
docker exec redis redis-cli -a changeme LLEN ingest_jobs

# Voir contenu
docker exec redis redis-cli -a changeme LRANGE ingest_jobs 0 -1
```

### Réinitialisation Complète

```powershell
# ⚠️ Supprime toutes les données
docker-compose down
docker volume rm $(docker volume ls -q | Select-String "projet_bigdata")
Remove-Item uploads\* -Exclude .gitkeep
docker-compose up -d
```

---

## 📈 Performances & Optimisations

### Capacités

| Métrique | Valeur |
|----------|--------|
| **Throughput** | 189 KB/s avg |
| **Latence API** | 51ms avg |
| **Fichier max** | 100 MB |
| **Workers** | 4 Gunicorn + 4 Celery |
| **Retry** | 3 tentatives |
| **Documents ES** | 36+ testés |

### Scalabilité

```yaml
# docker-compose.yml - Scaler services

# API replicas
flask-app:
  deploy:
    replicas: 3

# Plus de workers Celery
celery-worker:
  command: celery worker --concurrency=8

# RAM Elasticsearch
elasticsearch:
  environment:
    - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
```

---

## 📚 Documentation

- [ARCHITECTURE_DOCKER.md](ARCHITECTURE_DOCKER.md) - Comparaison localhost vs Docker
- [DOCKER_INGESTION_GUIDE.md](DOCKER_INGESTION_GUIDE.md) - Guide ingestion service
- [docs/architecture.md](docs/architecture.md) - Architecture détaillée
- [docs/api_documentation.md](docs/api_documentation.md) - API complète
- [docs/quick_start.md](docs/quick_start.md) - Démarrage rapide

---

## 🎯 Roadmap

- [ ] Authentification JWT
- [ ] Rate limiting
- [ ] Webhooks notifications
- [ ] Batch uploads
- [ ] Real-time streaming (WebSocket)
- [ ] ML anomaly detection
- [ ] Alerting (Slack/Email)
- [ ] Data retention policies
- [ ] Multi-tenant support
- [ ] Grafana dashboards

---

## ✅ Checklist Production

- [ ] Changer mots de passe `.env`
- [ ] Backup MongoDB (volumes)
- [ ] HTTPS (Nginx reverse proxy)
- [ ] Firewall Docker
- [ ] Log rotation
- [ ] Monitoring (Prometheus/Grafana)
- [ ] Alertes (PagerDuty)
- [ ] Disaster recovery tests
- [ ] Load testing"

---

**🎉 Système 100% Opérationnel et Testé !**

Pour questions : `docker-compose logs <service>` 😊
