# 🚀 Plateforme BigData - Analyse de Logs E-Commerce

Plateforme complète de centralisation, indexation et visualisation de logs e-commerce avec upload API, traitement automatique et dashboards temps réel.

## 📋 Réalisations Principales

### ✅ Infrastructure & DevOps
- Configuration Docker multi-services (Elasticsearch, Kibana, MongoDB, Redis, Logstash)
- Pipelines Logstash pour traitement JSON/CSV avec enrichissement GeoIP
- Configuration réseau et volumes persistants
- Health checks et monitoring des services

### ✅ Backend API (Flask)
- API REST complète avec endpoints CRUD pour logs
- Service d'upload de fichiers (JSON/CSV, max 100MB)
- Service de recherche avancée avec filtres multiples
- Service de gestion des recherches sauvegardées
- Intégration Elasticsearch, MongoDB et Redis
- Workers Celery pour traitement asynchrone
- Validation et sanitization des données

### ✅ Frontend Web
- Refactoring complet avec système de templates Jinja2 (base.html)
- Dashboard temps réel avec Chart.js (KPIs, graphiques, métriques)
- Page de recherche avancée avec Flatpickr date picker
- Page d'upload avec drag & drop et validation
- Page de résultats avec pagination, tri et export CSV/JSON
- **Route /kibana avec iframe embarqué pour visualisations**
- Design responsive avec Tailwind CSS et Font Awesome
- Navigation unifiée et footer informatif

### ✅ Visualisations Kibana
- Création de 3 visualisations exportées :
  - **Logs par Heure** : Line chart des logs/erreurs sur 24h
  - **Top Erreurs** : Bar chart des messages d'erreur par service
  - **Distribution Montants** : Donut chart des montants de transactions
- **Dashboard Kibana unifié** (`ecommerce-logs-dashboard`) combinant les 3 visualisations
- Import automatisé via API Saved Objects
- Configuration CORS et X-Frame-Options pour embedding iframe

### ✅ Corrections & Optimisations
- Fix bug double-click upload (event propagation)
- Fix erreurs JavaScript dashboard (null checks, optional chaining)
- Correction mappings champs Elasticsearch (event.original, service, amount)
- Configuration Kibana pour permettre iframe embedding
- Suppression fichiers obsolètes (*_old.html)

### ✅ Documentation
- README complet avec stack technique et API endpoints
- Guide d'intégration Kibana (KIBANA_INTEGRATION.md)
- Instructions d'import des visualisations
- Troubleshooting et recommandations de sécurité

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

## 🚀 Démarrage Rapide

```powershell
# 1. Cloner et configurer
cd c:\projet_bigdata
Copy-Item .env.example .env

# 2. Démarrer tous les services
docker-compose up -d

# 3. Vérifier le statut (~60s)
docker-compose ps
```

## 🌐 Services Disponibles

| Service | URL | Description |
|---------|-----|-------------|
| Dashboard | http://localhost:5001/dashboard | Visualisation temps réel |
| Search | http://localhost:5001/search | Recherche avancée logs |
| Upload | http://localhost:5001/upload | Upload fichiers JSON/CSV |
| Results | http://localhost:5001/results | Affichage résultats avec export |
| **Kibana** | **http://localhost:5001/kibana** | **Dashboard Kibana embarqué (nouveau)** |
| API | http://localhost:5001/api | REST API endpoints |
| Kibana Direct | http://localhost:5601 | Accès direct Kibana |

## 📡 API Endpoints Principaux

### Upload de Fichiers
```bash
# POST /api/logs/upload
curl -X POST http://localhost:5001/api/logs/upload -F "file=@logs.json"
```
**Formats acceptés** : JSON, CSV (max 100 MB)

### Recherche Logs
```bash
# POST /api/logs/search
curl -X POST http://localhost:5001/api/logs/search \
  -H "Content-Type: application/json" \
  -d '{"level":"ERROR","service":"payment","size":50}'
```

**Filtres disponibles** :
- `query` : Recherche texte libre
- `level` : Niveau de log (ERROR, WARNING, INFO, DEBUG, CRITICAL)
- `service` : Nom du service
- `date_from` / `date_to` : Plage de dates (format: `YYYY-MM-DD HH:MM`)
- `size` : Nombre de résultats (défaut: 100)

### Services Disponibles
```bash
# GET /api/logs/search/services
curl http://localhost:5001/api/logs/search/services
```

### Sauvegarder une Recherche
```bash
# POST /api/logs/search/save
curl -X POST http://localhost:5001/api/logs/search/save \
  -H "Content-Type: application/json" \
  -d '{"name":"Erreurs Payment","filters":{"level":"ERROR","service":"payment"}}'
```

### Recherches Récentes
```bash
# GET /api/logs/search/recent?limit=5
curl http://localhost:5001/api/logs/search/recent?limit=5
```

## 🎨 Dashboard Features

### KPIs Temps Réel
- Total logs avec croissance %
- Erreurs totales + taux d'erreur
- Utilisateurs uniques + actifs
- Temps de réponse moyen

### Visualisations Chart.js
- **Timeline** : Logs par heure (24h) avec erreurs
- **Distribution** : Répartition par niveau (INFO, ERROR, WARNING, etc.)
- **Top Services** : Classement des services par volume
- **Erreurs Récentes** : Tableau des 10 dernières erreurs

### Dashboard Kibana Embarqué (Nouveau)
- **Iframe intégré** dans l'interface Flask à `/kibana`
- **3 visualisations combinées** :
  - Logs par heure avec distinction erreurs/normal
  - Top 10 messages d'erreur par service
  - Distribution des montants de transactions
- **Boutons interactifs** : Rafraîchir, Ouvrir en pleine page
- **Configuration CORS** pour embedding sécurisé

## 🔍 Page de Recherche

**Features** :
- Recherche texte libre multi-champs
- Filtres : niveau, service, date range
- Date picker avec filtres rapides (1h, 24h, 7j, 30j)
- Sauvegarde des recherches
- Export JSON/CSV
- Affichage détail complet de chaque log

## 📁 Structure du Projet

```
projet_bigdata/
├── backend/
│   ├── app/
│   │   ├── routes/          # API endpoints (logs, search, dashboard, analytics)
│   │   ├── services/        # Business logic (ES, Mongo, Redis, Dashboard)
│   │   ├── templates/       # Pages HTML (dashboard, search, upload, results, kibana)
│   │   └── __init__.py
│   ├── main.py
│   └── requirements.txt
├── infra/
│   ├── logstash/pipelines/  # Pipelines JSON/CSV
│   └── kibana/config/       # Configuration Kibana (CORS, iframe)
├── kibana_exports/          # Visualisations & dashboard .ndjson
├── uploads/                 # Fichiers uploadés
├── docker-compose.yml       # 8 services
├── KIBANA_INTEGRATION.md    # Documentation intégration Kibana
└── .env                     # Configuration
```

## ⚙️ Configuration (.env)

```bash
# Elasticsearch
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200

# MongoDB
MONGODB_URI=mongodb://admin:changeme@mongodb:27017/ecommerce_logs

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Upload
MAX_FILE_SIZE_MB=100
ALLOWED_EXTENSIONS=csv,json
```

> ⚠️ **Production** : Changez les mots de passe par défaut !

## 🔄 Workflow

1. **Upload** : Fichier CSV/JSON via API ou interface web
2. **Validation** : Extension, taille, contenu
3. **Queue** : Job ajouté dans Redis
4. **Traitement** : Logstash parse et enrichit (GeoIP)
5. **Indexation** : Elasticsearch stocke dans `logs-ecom-*`
6. **Visualisation** : Dashboard Flask (Chart.js) + Kibana (iframe embarqué)

## 📊 Kibana Visualizations

### Visualisations Disponibles
- `logs-per-hour-viz` : Line chart logs/erreurs 24h
- `top-error-messages-viz` : Bar chart top 10 erreurs
- `transaction-amount-distribution-viz` : Donut chart montants

### Dashboard Unifié
- `ecommerce-logs-dashboard` : Combine les 3 visualisations
- Accessible via `/kibana` (iframe) ou directement sur Kibana
- Import automatisé via API Saved Objects

### Import Manuel (si nécessaire)
```powershell
docker cp kibana_exports/ecommerce_dashboard.ndjson kibana:/tmp/
docker exec kibana curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" -H "kbn-xsrf: true" -F "file=@/tmp/ecommerce_dashboard.ndjson"
```

## 🔧 Commandes Utiles

```powershell
# Logs temps réel
docker-compose logs -f flask-app

# Redémarrer un service
docker-compose restart flask-app
docker-compose restart kibana  # Après modification config

# Vérifier la queue Redis
docker exec redis redis-cli -a changeme LLEN ingest_jobs

# Compter les documents Elasticsearch
Invoke-RestMethod -Uri "http://localhost:9200/logs-ecom-*/_count"

# Health check
Invoke-RestMethod -Uri "http://localhost:5001/api/health"

# Vérifier les visualisations Kibana
Invoke-RestMethod -Uri "http://localhost:5601/api/saved_objects/_find?type=visualization"
```

## 🐛 Troubleshooting

**Service unhealthy** :
```powershell
docker-compose logs <service>
docker-compose restart <service>
```

**Pas d'indexation Elasticsearch** :
```powershell
docker-compose logs logstash | Select-String "processed"
docker-compose restart logstash
```

**Réinitialisation complète** :
```powershell
docker-compose down
docker volume prune -f
docker-compose up -d
```

## 📊 Performances

| Métrique | Valeur |
|----------|--------|
| **Throughput** | ~190 KB/s |
| **Latence API** | <52ms |
| **Fichier max** | 100 MB |
| **Formats** | JSON, CSV |

---

**🎉 Système opérationnel et testé !**

### 📚 Documentation Complémentaire
- **KIBANA_INTEGRATION.md** : Guide complet intégration Kibana avec iframe
- **kibana_exports/README_IMPORT.md** : Instructions import visualisations

Pour plus d'infos : `docker-compose logs <service>`
