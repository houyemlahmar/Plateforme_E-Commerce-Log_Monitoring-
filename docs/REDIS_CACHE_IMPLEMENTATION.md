# 🚀 Implémentation du Cache Redis pour Elasticsearch

## Vue d'ensemble

Le système de cache Redis optimise les performances des recherches Elasticsearch en mettant en cache les résultats des requêtes fréquentes.

## ✅ Fonctionnalités implémentées

### 1. Génération de clé de cache

**Fichier**: `backend/app/services/search_service.py`

```python
def _generate_cache_key(self, **params):
    """
    Génère une clé de cache unique basée sur les paramètres de recherche
    
    - Trie les paramètres pour cohérence
    - Filtre les valeurs None
    - Génère un hash MD5
    - Format: search:<hash>
    """
    sorted_params = sorted(params.items())
    filtered_params = [(k, v) for k, v in sorted_params if v is not None]
    params_str = json.dumps(filtered_params, sort_keys=True)
    hash_obj = hashlib.md5(params_str.encode())
    return f"search:{hash_obj.hexdigest()}"
```

**Exemple de clé**: `search:66cf40faa150b0e121444428e6a186ec`

### 2. Stockage des résultats avec TTL

**TTL configuré**: 60 secondes par défaut

```python
# Cache results with 60 seconds TTL
self.redis_service.set(cache_key, search_results, ttl=60)
logger.debug(f"Cached search results: {cache_key}")
```

**Données mises en cache**:
- Résultats de recherche complets
- Métadonnées de pagination (total, page, total_pages)
- Filtres appliqués
- Paramètres de tri

### 3. Lecture depuis le cache

```python
# Try to get from cache
cached_result = self.redis_service.get(cache_key)
if cached_result:
    logger.info(f"Cache HIT for search: {cache_key}")
    cached_result['cached'] = True
    return cached_result

logger.info(f"Cache MISS for search: {cache_key}")
```

**Indicateur dans la réponse**:
```json
{
  "cached": true,
  "total": 40,
  "results": [...],
  "page": 1
}
```

### 4. Invalidation du cache

**Fichier**: `backend/app/services/redis_service.py`

```python
def delete_pattern(self, pattern):
    """
    Supprime toutes les clés correspondant à un pattern
    Utilise SCAN pour itérer efficacement
    """
    deleted_count = 0
    cursor = 0
    
    while True:
        cursor, keys = self.client.scan(cursor, match=pattern, count=100)
        if keys:
            deleted_count += self.client.delete(*keys)
        if cursor == 0:
            break
    
    logger.info(f"Deleted {deleted_count} keys matching pattern: {pattern}")
    return deleted_count
```

**Déclencheurs d'invalidation**:

1. **Upload de fichier** (`process_upload_with_preview`):
```python
# Invalidate search cache on new upload
self.redis_service.delete_pattern('search:*')
logger.info("Invalidated all search caches due to new upload")
```

2. **Traitement de logs** (`process_log_file`):
```python
# Invalidate cache
self.redis_service.delete('logs:recent')
self.redis_service.delete('logs:stats')
self.redis_service.delete_pattern('search:*')
```

3. **Ingestion de logs** (`ingest_logs`):
```python
# Invalidate cache
self.redis_service.delete_pattern('search:*')
logger.info("Invalidated caches due to log ingestion")
```

## 📊 Performances mesurées

### Tests de performance

```
Test 1: Première recherche (CACHE MISS)
  Temps: 205ms
  Cached: False
  Résultats: 40 logs

Test 2: Même recherche (CACHE HIT)
  Temps: 43ms
  Cached: True
  Résultats: 40 logs

Amélioration: 78.9% 🚀
```

### Logs Redis

```
INFO - Cache MISS for search: search:66cf40faa150b0e121444428e6a186ec
INFO - Executing search: query='payment', page=1, size=20
INFO - Cache HIT for search: search:66cf40faa150b0e121444428e6a186ec
INFO - Cache HIT for search: search:66cf40faa150b0e121444428e6a186ec
```

## 🔧 Configuration

### Variables d'environnement

```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=changeme
```

### Configuration du cache

```python
# dans RedisService.__init__
self.cache_ttl = config.get('cache_ttl', 3600)  # 1 heure par défaut

# dans SearchService.search
self.redis_service.set(cache_key, search_results, ttl=60)  # 60 secondes pour les recherches
```

## 📝 Intégration dans l'API

### Endpoint de recherche

**Route**: `POST /api/logs/search`

**Avant optimisation**:
```python
# Direct Elasticsearch query (sans cache)
result = current_app.es_service.search('logs', query)
```

**Après optimisation**:
```python
# Utilisation du SearchService avec cache
search_service = SearchService(
    current_app.es_service,
    current_app.redis_service,
    current_app.mongo_service
)

search_results = search_service.search(
    query=query_text,
    level=level,
    service=service,
    ...
)
```

### Réponse API enrichie

```json
{
  "success": true,
  "results": [...],
  "total": 40,
  "count": 10,
  "cached": true,
  "page": 1,
  "total_pages": 4
}
```

## 🐛 Corrections apportées

### 1. QueryBuilder - Champs numériques

**Problème**: Les champs `user_id`, `order_id`, `transaction_id` sont de type `long` dans Elasticsearch mais traités comme texte avec fuzzy matching.

**Solution**: 
- Retrait des champs numériques du `multi_match`
- Traitement spécial pour `user_id` dans les filtres

```python
# Avant
"fields": [
    "message^3",
    "user_id",      # ❌ Cause fuzzy query error
    "order_id",     # ❌ Type long
    "transaction_id" # ❌ Type long
]

# Après
"fields": [
    "message^3",
    "error_message^2",
    "endpoint",
    "service"
]
```

### 2. Filtre user_id adaptatif

```python
def with_user_filter(self, user_id):
    try:
        # Essayer conversion en int pour type long
        user_id_value = int(user_id_clean)
        self.query["query"]["bool"]["filter"].append({
            "term": {"user_id": user_id_value}
        })
    except ValueError:
        # Sinon traiter comme keyword
        self.query["query"]["bool"]["filter"].append({
            "term": {"user_id.keyword": user_id_clean}
        })
```

## 🧪 Tests

### Test manuel avec curl

```bash
# Première recherche (MISS)
curl -X POST http://localhost:5001/api/logs/search \
  -H "Content-Type: application/json" \
  -d '{"query":"error","size":10}'

# Deuxième recherche (HIT)
curl -X POST http://localhost:5001/api/logs/search \
  -H "Content-Type: application/json" \
  -d '{"query":"error","size":10}'
```

### Test d'invalidation

```bash
# 1. Recherche pour remplir le cache
curl -X POST http://localhost:5001/api/logs/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test","size":10}'

# 2. Upload d'un fichier (invalide le cache)
curl -X POST http://localhost:5001/api/logs/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@test_logs.json"

# 3. Même recherche (MISS car cache invalidé)
curl -X POST http://localhost:5001/api/logs/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test","size":10}'
```

### Vérification des clés Redis

```bash
# Connexion à Redis
docker exec -it redis redis-cli

# Liste des clés de cache
KEYS search:*

# Voir une clé spécifique
GET search:66cf40faa150b0e121444428e6a186ec

# TTL d'une clé
TTL search:66cf40faa150b0e121444428e6a186ec
```

## ✅ Critères d'acceptation

| Critère | Statut | Détails |
|---------|--------|---------|
| ✅ Génération de clé basée sur paramètres | Validé | MD5 hash avec tri des paramètres |
| ✅ Stockage avec TTL configurable | Validé | 60s pour recherches, 3600s par défaut |
| ✅ Lecture depuis cache si disponible | Validé | Indicateur `cached` dans réponse |
| ✅ Invalidation lors d'uploads | Validé | Pattern `search:*` supprimé |
| ✅ Requêtes répétées plus rapides | Validé | **78.9% d'amélioration** |
| ✅ Redis effectivement utilisé | Validé | Logs confirmés (HIT/MISS) |

## 📈 Impact

### Avant
- Toutes les recherches interrogent Elasticsearch
- Temps de réponse: ~200ms par recherche
- Charge élevée sur Elasticsearch

### Après
- Première recherche: ~200ms (MISS)
- Recherches suivantes: ~40ms (HIT)
- **Réduction de 78.9% du temps de réponse**
- **Réduction de la charge Elasticsearch**

## 🔮 Améliorations futures

1. **Cache stratifié**:
   - Court terme: 60s pour résultats volatiles
   - Long terme: 1h pour agrégations
   
2. **Invalidation sélective**:
   - Invalider uniquement les recherches concernées
   - Conserver les caches non affectés

3. **Statistiques de cache**:
   - Hit rate monitoring
   - Cache size tracking
   - Performance analytics

4. **Pre-warming**:
   - Pré-charger les recherches fréquentes
   - Cache des top 10 queries

## 📚 Références

- **Redis**: `backend/app/services/redis_service.py`
- **SearchService**: `backend/app/services/search_service.py`
- **LogService**: `backend/app/services/log_service.py`
- **Routes**: `backend/app/routes/logs_routes.py`
- **QueryBuilder**: `backend/app/utils/query_builder.py`

---

**Version**: 2.0.0  
**Date**: Janvier 2026  
**Statut**: ✅ Production Ready
