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
| API | http://localhost:5001/api | REST API endpoints |
| Kibana | http://localhost:5601 | Visualisation Elasticsearch |

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

### Visualisations
- **Timeline** : Logs par heure (24h) avec erreurs
- **Distribution** : Répartition par niveau (INFO, ERROR, WARNING, etc.)
- **Top Services** : Classement des services par volume
- **Erreurs Récentes** : Tableau des 10 dernières erreurs

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
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── templates/       # HTML pages (dashboard, search, upload)
│   │   └── __init__.py
│   ├── main.py
│   └── requirements.txt
├── infra/
│   └── logstash/pipelines/  # Pipelines JSON/CSV
├── uploads/                 # Fichiers uploadés
├── docker-compose.yml       # 8 services
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
6. **Visualisation** : Dashboard + Kibana

## 🔧 Commandes Utiles

```powershell
# Logs temps réel
docker-compose logs -f flask-app

# Redémarrer un service
docker-compose restart flask-app

# Vérifier la queue Redis
docker exec redis redis-cli -a changeme LLEN ingest_jobs

# Compter les documents Elasticsearch
Invoke-RestMethod -Uri "http://localhost:9200/logs-ecom-*/_count"

# Health check
Invoke-RestMethod -Uri "http://localhost:5001/api/health"
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

Pour plus d'infos : `docker-compose logs <service>`
