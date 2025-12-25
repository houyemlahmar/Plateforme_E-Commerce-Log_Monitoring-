# Architecture : localhost vs hostnames Docker

## 🔍 Différence

### Option 1 : localhost (exécution hors Docker)
```python
REDIS_HOST=localhost       # Port exposé 6379
MONGODB_HOST=localhost     # Port exposé 27017
```
- **Usage** : Code Python tourne sur Windows
- **Connexion** : Via ports exposés par Docker
- **Fichier** : `.env.local` nécessaire
- **Commande** : `python backend/ingestion_service.py`

### Option 2 : redis/mongodb (exécution dans Docker) ✅
```python
REDIS_HOST=redis           # Réseau Docker interne
MONGODB_HOST=mongodb       # Réseau Docker interne
```
- **Usage** : Code Python tourne dans container
- **Connexion** : Via réseau Docker `elk-network`
- **Fichier** : `.env` suffit
- **Commande** : `docker-compose up -d`

## ✅ Choix Retenu : Docker (redis/mongodb)

### Pourquoi ?

#### 1. **Cohérence environnements**
```
Dev  : docker-compose up -d
Prod : docker-compose up -d
Test : docker-compose up -d
```
Même setup partout = zéro surprise

#### 2. **Simplicité déploiement**
```yaml
# docker-compose.yml contient TOUT
services:
  - elasticsearch
  - flask-app
  - ingestion-service  # Ici !
```
Une commande pour tout démarrer

#### 3. **Réseau optimisé**
```
Container → Container communication
├── Pas de localhost:port
├── Pas de firewall Windows
└── Latence minimale
```

#### 4. **Configuration unifiée**
```bash
# .env pour TOUS les services
REDIS_HOST=redis
MONGODB_HOST=mongodb
```

#### 5. **Production-ready**
- Restart automatique : `restart: unless-stopped`
- Health checks intégrés
- Logs centralisés : `docker-compose logs`
- Scaling facile : `docker-compose scale ingestion-service=3`

### Comparaison Complète

| Critère | localhost | Docker |
|---------|-----------|--------|
| **Setup** | Python + dépendances locales | `docker-compose build` |
| **Démarrage** | `python ingestion_service.py` | `docker-compose up -d` |
| **Config** | 2 fichiers (.env + .env.local) | 1 fichier (.env) |
| **Réseau** | localhost:6379, localhost:27017 | redis:6379, mongodb:27017 |
| **Ports** | Doit exposer tous les ports | Ports internes uniquement |
| **Dépendances** | pip install sur Windows | Image Docker isolée |
| **Logs** | Fichier local | `docker-compose logs` |
| **Restart auto** | Non (script batch) | Oui (`restart: unless-stopped`) |
| **Dev = Prod** | ❌ Non | ✅ Oui |
| **Maintenance** | Gérer 2 environnements | 1 seul environnement |
| **Scaling** | Difficile | `docker-compose scale` |
| **CI/CD** | Config spéciale | Même docker-compose |

## 🏗️ Architecture Actuelle

```
┌─────────────────────────────────────────┐
│         Docker Network (elk-network)    │
│                                          │
│  ┌──────────┐    ┌──────────┐          │
│  │  redis   │◄───┤ ingestion │          │
│  │  :6379   │    │  service  │          │
│  └──────────┘    └─────┬─────┘          │
│                        │                 │
│  ┌──────────┐         │                 │
│  │ mongodb  │◄────────┘                 │
│  │ :27017   │                           │
│  └──────────┘                           │
│                                          │
│  ┌──────────┐    ┌──────────┐          │
│  │flask-app │    │logstash  │          │
│  └────┬─────┘    └──────────┘          │
│       │                                  │
└───────┼──────────────────────────────────┘
        │
        ▼ Port exposé
  localhost:5001 (Windows)
```

**Communication interne** : Via noms de service (`redis`, `mongodb`)  
**Accès externe** : Via ports exposés (`localhost:6379`, `localhost:27017`)

## 📊 Bénéfices Mesurables

### Avant (localhost)
```bash
# Terminal 1
cd backend
python ingestion_service.py

# Si ça crash → perte de jobs
# Si reboot Windows → service down
# Dev ≠ Prod → bugs en production
```

### Après (Docker)
```bash
# Une seule commande
docker-compose up -d

# Crash → restart auto
# Reboot → démarre avec Docker
# Dev = Prod → aucune surprise
```

## 🎯 Recommandations

### Pour Développement
✅ **Utiliser Docker** même en dev
- Commande : `docker-compose up -d`
- Logs : `docker-compose logs -f ingestion-service`
- Debug : `docker-compose exec ingestion-service bash`

### Pour Production
✅ **Même docker-compose.yml**
- Changer seulement les mots de passe dans `.env`
- Ajouter monitoring (Prometheus, Grafana)
- Configurer backups volumes

### Pour Tests
✅ **Environnement isolé**
```bash
# Environnement test séparé
docker-compose -f docker-compose.test.yml up -d
```

## 📝 Migration

Si vous aviez l'ancien système (localhost) :

### Étapes
1. ✅ Supprimer `.env.local`
2. ✅ Utiliser `.env` avec hostnames Docker
3. ✅ Build image : `docker-compose build ingestion-service`
4. ✅ Démarrer : `docker-compose up -d ingestion-service`
5. ✅ Vérifier : `docker-compose logs ingestion-service`

### Résultat
```bash
# Avant : 2 systèmes à gérer
python ingestion_service.py        # Local
docker-compose up -d                # Autres services

# Après : 1 seul système
docker-compose up -d                # TOUT
```

## 🎉 Conclusion

**Docker (redis/mongodb)** est le choix optimal pour :
- ✅ Production
- ✅ Développement
- ✅ Tests
- ✅ CI/CD

**localhost** uniquement pour :
- ❌ Debug ponctuel (rare)
- ❌ Développement sans Docker (déconseillé)

**Notre projet utilise 100% Docker** = simplicité + fiabilité + production-ready ! 🚀
