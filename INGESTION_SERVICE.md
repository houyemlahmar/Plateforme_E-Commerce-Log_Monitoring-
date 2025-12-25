# Ingestion Service Implementation

## 📋 Overview

Service Python autonome qui écoute la queue Redis `ingest_jobs`, déplace les fichiers vers le répertoire surveillé par Logstash, et met à jour les statuts dans MongoDB.

## ✅ Implémentation Complète

### 1. Service Principal
**Fichier**: [`backend/ingestion_service.py`](backend/ingestion_service.py)

**Fonctionnalités**:
- ✅ Écoute en continu de la liste Redis `ingest_jobs`
- ✅ Déplacement des fichiers vers le répertoire Logstash (`./uploads`)
- ✅ Mise à jour des statuts dans MongoDB collection `uploads`
- ✅ Logique de retry (3 tentatives par défaut, délai 5s)
- ✅ Logging complet (fichier + console)
- ✅ Gestion gracieuse des signaux (SIGINT, SIGTERM)
- ✅ Gestion d'erreurs robuste

**Statuts MongoDB**:
- `pending` - Job créé, en attente
- `processing` - En cours de traitement
- `completed` - Traitement réussi
- `failed` - Échec après tous les retries

### 2. Script de Démarrage
**Fichier**: [`backend/start_ingestion_service.py`](backend/start_ingestion_service.py)

Simple wrapper pour démarrer le service avec affichage des informations.

### 3. Tests Automatisés
**Fichier**: [`test_ingestion_service.py`](test_ingestion_service.py)

**Tests inclus**:
1. ✅ Vérification statut queue Redis
2. ✅ Vérification collection MongoDB `uploads`
3. ✅ Création fichier de test
4. ✅ Push job dans la queue
5. ✅ Workflow complet (upload API → queue → ingestion)

## 🚀 Utilisation

### Démarrer le Service

```powershell
# Méthode 1: Directement
cd backend
python start_ingestion_service.py

# Méthode 2: Via module
cd backend
python -m ingestion_service
```

**Sortie**:
```
============================================================
Starting Ingestion Service
============================================================

This service will:
  - Listen to Redis queue 'ingest_jobs'
  - Move files to Logstash watch directory
  - Update job status in MongoDB

Press Ctrl+C to stop

============================================================
2025-12-25 10:00:00 - INFO - Ingestion Service initialized
2025-12-25 10:00:00 - INFO - Source directory: C:\projet_bigdata\uploads
2025-12-25 10:00:00 - INFO - Target directory: C:\projet_bigdata\uploads
2025-12-25 10:00:00 - INFO - Starting ingestion service listener...
```

### Tester le Service

```powershell
# Lancer les tests
python test_ingestion_service.py
```

## 🔄 Workflow Complet

```
1. Upload fichier via API
   POST /api/logs/upload
   └─> Fichier sauvegardé dans ./uploads/TIMESTAMP_UUID_filename
   └─> Métadonnées dans MongoDB collection "uploads" (status: pending)
   └─> Job pusher dans Redis queue "ingest_jobs"

2. Service Ingestion (écoute en continu)
   └─> Pop job depuis Redis queue "ingest_jobs" (FIFO)
   └─> Update status MongoDB: "processing"
   └─> Déplace/vérifie fichier dans ./uploads (watch dir Logstash)
   └─> Update status MongoDB: "completed" ou "failed"
   └─> Retry automatique en cas d'échec (max 3 fois)

3. Logstash (surveillance automatique)
   └─> Détecte nouveau fichier dans ./uploads
   └─> Parse selon pipeline (JSON ou CSV)
   └─> Index dans Elasticsearch
   └─> Fichier traité reste dans ./uploads (ou archivé)
```

## ⚙️ Configuration

### Paramètres Service
Dans [`backend/ingestion_service.py`](backend/ingestion_service.py#L35):

```python
IngestionService(
    redis_service=redis_service,
    mongo_service=mongo_service,
    source_dir='./uploads',        # Répertoire source
    target_dir='./uploads',        # Répertoire Logstash (même dir)
    max_retries=3,                 # Nombre de retries
    retry_delay=5,                 # Délai entre retries (secondes)
    poll_interval=5                # Fréquence polling queue (secondes)
)
```

### Logging
Logs écrits dans:
- **Fichier**: `backend/ingestion_service.log`
- **Console**: stdout (temps réel)

Format:
```
2025-12-25 10:05:30 - ingestion_service - INFO - Processing job abc123: ./uploads/file.json
2025-12-25 10:05:31 - ingestion_service - INFO - File already in Logstash watch directory: file.json
2025-12-25 10:05:31 - ingestion_service - INFO - Job abc123 completed successfully
```

## 🔍 Monitoring

### Vérifier la Queue Redis
```powershell
# Longueur de la queue
docker-compose exec redis redis-cli -a redis_password LLEN ingest_jobs

# Voir les jobs (premiers 10)
docker-compose exec redis redis-cli -a redis_password LRANGE ingest_jobs 0 9

# Vider la queue (si nécessaire)
docker-compose exec redis redis-cli -a redis_password DEL ingest_jobs
```

### Vérifier MongoDB
```powershell
# Voir tous les uploads
docker-compose exec mongodb mongosh -u admin -p mongodb_password --eval "use ecommerce_logs; db.uploads.find().pretty()"

# Compter par statut
docker-compose exec mongodb mongosh -u admin -p mongodb_password --eval "use ecommerce_logs; db.uploads.aggregate([{$group: {_id: '$status', count: {$sum: 1}}}])"

# Uploads en erreur
docker-compose exec mongodb mongosh -u admin -p mongodb_password --eval "use ecommerce_logs; db.uploads.find({status: 'failed'}).pretty()"
```

### Logs du Service
```powershell
# Voir les logs en temps réel
Get-Content backend\ingestion_service.log -Wait

# Dernières 50 lignes
Get-Content backend\ingestion_service.log -Tail 50
```

## 🛠️ Retry Logic

Le service implémente une stratégie de retry robuste:

1. **Première tentative**: Traitement immédiat
2. **Échec**: Attente 5 secondes → Retry 1
3. **Échec**: Attente 5 secondes → Retry 2
4. **Échec**: Attente 5 secondes → Retry 3
5. **Échec final**: Marque job comme `failed` dans MongoDB

**Informations MongoDB en cas d'échec**:
```json
{
  "job_id": "abc-123",
  "status": "failed",
  "error_message": "Max retries exceeded: File not found",
  "retry_count": 3,
  "failed_at": "2025-12-25T10:05:45Z"
}
```

## 📊 Métriques & Stats

Le service log les métriques suivantes:
- Nombre de jobs traités
- Temps de traitement par job
- Nombre de retries
- Taux de succès/échec
- Longueur de la queue

## 🐛 Troubleshooting

### Service ne démarre pas
```powershell
# Vérifier Redis
docker-compose exec redis redis-cli -a redis_password PING

# Vérifier MongoDB
docker-compose exec mongodb mongosh -u admin -p mongodb_password --eval "db.adminCommand('ping')"

# Vérifier config
python -c "from backend.config import get_config; print(get_config().REDIS_CONFIG)"
```

### Jobs bloqués dans la queue
```powershell
# Voir les jobs
docker-compose exec redis redis-cli -a redis_password LRANGE ingest_jobs 0 -1

# Redémarrer le service avec logs détaillés
cd backend
python start_ingestion_service.py
```

### Fichiers non traités par Logstash
```powershell
# Vérifier que Logstash surveille le bon répertoire
docker-compose exec logstash cat /usr/share/logstash/pipeline/pipeline_json.conf | grep "path =>"

# Voir logs Logstash
docker-compose logs -f logstash | Select-String "processed"

# Vérifier permissions fichiers
Get-ChildItem uploads\ | Select-Object Name, Length, LastWriteTime
```

## 🔐 Sécurité & Production

### Recommandations
1. **Permissions fichiers**: Limiter accès à `./uploads/`
2. **Validation**: Le service vérifie l'existence des fichiers
3. **Error handling**: Toutes les exceptions sont catchées et loggées
4. **Graceful shutdown**: Signal handlers pour arrêt propre
5. **Monitoring**: Configurer alertes sur logs `ERROR` et `CRITICAL`

### Déploiement Production
```powershell
# En tant que service Windows (avec NSSM)
nssm install IngestionService "C:\Python\python.exe" "C:\projet_bigdata\backend\start_ingestion_service.py"
nssm set IngestionService AppDirectory "C:\projet_bigdata\backend"
nssm start IngestionService

# Ou avec Task Scheduler (démarrage automatique)
```

## 📝 Fichiers Supprimés

- ❌ `backend/app/tasks/log_tasks.py` - Tâches Celery incomplètes, remplacées par service autonome
- ✅ Service autonome plus simple et robuste sans dépendance Celery

## 🎯 Avantages du Service Autonome

Comparé aux tâches Celery:
- ✅ **Plus simple**: Pas besoin de Celery worker
- ✅ **Plus rapide**: Écoute en continu (polling 5s vs déclenchement manuel)
- ✅ **Plus robuste**: Retry logic intégrée
- ✅ **Meilleur monitoring**: Logs détaillés en temps réel
- ✅ **Graceful shutdown**: Gestion propre des signaux
- ✅ **Standalone**: Peut tourner indépendamment de Flask

## 📚 Références

- Code source: [`backend/ingestion_service.py`](backend/ingestion_service.py)
- Tests: [`test_ingestion_service.py`](test_ingestion_service.py)
- Démarrage: [`backend/start_ingestion_service.py`](backend/start_ingestion_service.py)
