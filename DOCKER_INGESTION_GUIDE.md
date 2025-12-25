# 🚀 Démarrage du Service Ingestion (Docker)

## ✅ Architecture : Tout dans Docker

**Choix retenu** : Service d'ingestion dans Docker (meilleure pratique)
- ✅ Cohérence : tous les services containerisés
- ✅ Simplicité : une seule commande `docker-compose up`
- ✅ Production-ready : même setup dev/prod
- ✅ Isolation : pas de dépendances locales

## 🎯 Démarrage

### Build et démarrer tous les services (incluant ingestion)
```powershell
cd C:\projet_bigdata

# Build nouveau service
docker-compose build ingestion-service

# Démarrer tous les services
docker-compose up -d

# Vérifier
docker-compose ps
```

Vous devriez voir **8 services** actifs :
- elasticsearch
- kibana
- logstash
- mongodb
- redis
- flask-app
- celery-worker
- **ingestion-service** ✨ (nouveau)

## 📊 Monitoring

### Logs du service d'ingestion
```powershell
# Voir les logs en temps réel
docker-compose logs -f ingestion-service

# Dernières 50 lignes
docker-compose logs --tail=50 ingestion-service
```

**Sortie attendue** :
```
ingestion-service | Successfully connected to Redis
ingestion-service | Successfully connected to MongoDB
ingestion-service | Ingestion Service initialized
ingestion-service | Starting ingestion service listener...
```

### Vérifier la queue Redis
```powershell
docker-compose exec redis redis-cli -a changeme LLEN ingest_jobs
```

### Vérifier MongoDB
```powershell
docker-compose exec mongodb mongosh -u admin -p changeme --eval "use ecommerce_logs; db.uploads.countDocuments()"
```

## 🧪 Test Workflow Complet

```powershell
# 1. Créer fichier test
@"
{"timestamp":"2025-12-25T14:00:00Z","log_type":"docker_test","message":"Test from Docker"}
"@ | Out-File -FilePath uploads\docker_test.json -Encoding utf8

# 2. Upload via API
curl -X POST http://localhost:5001/api/logs/upload -F "file=@uploads\docker_test.json"

# 3. Observer le traitement (temps réel)
docker-compose logs -f ingestion-service

# Vous verrez:
# - Found 1 jobs in queue
# - Processing job abc123
# - Job completed successfully

# 4. Vérifier Elasticsearch (~30s)
curl http://localhost:9200/logs-ecom-*/_search?size=5
```

## 🔧 Gestion du Service

### Redémarrer uniquement ingestion
```powershell
docker-compose restart ingestion-service
```

### Rebuild après modification code
```powershell
docker-compose build ingestion-service
docker-compose up -d ingestion-service
```

### Arrêter temporairement
```powershell
docker-compose stop ingestion-service
```

### Démarrer après arrêt
```powershell
docker-compose start ingestion-service
```

## 🆚 Comparaison : Local vs Docker

| Aspect | Local (localhost) | Docker (redis/mongodb) |
|--------|------------------|----------------------|
| Configuration | `.env.local` nécessaire | `.env` suffit |
| Démarrage | `python start_ingestion_service.py` | `docker-compose up -d` |
| Connexions | localhost:6379, localhost:27017 | redis:6379, mongodb:27017 |
| Isolation | Dépendances Python locales | Container isolé |
| Production | Différent du dev | Identique |
| Maintenance | 2 environnements à gérer | 1 seul environnement |
| **Recommandation** | ❌ Dev uniquement | ✅ **Production-ready** |

## ✨ Avantages Solution Docker

1. **Un seul fichier** : `docker-compose.yml` contient tout
2. **Pas de configuration locale** : Fonctionne partout
3. **Redémarrage auto** : `restart: unless-stopped`
4. **Logs centralisés** : `docker-compose logs`
5. **Scaling facile** : `docker-compose scale ingestion-service=3`
6. **Même setup dev/prod** : Pas de surprises

## 📝 Services Déployés

```
8 services actifs dans Docker :
├── elasticsearch    (9200)
├── kibana          (5601)
├── logstash        (5000, 5044)
├── mongodb         (27017)
├── redis           (6379)
├── flask-app       (5001)
├── celery-worker   (4 workers)
└── ingestion-service ✨ (traite queue Redis)
```

Tout communique via le réseau Docker `elk-network` 🎉
