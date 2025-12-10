# Guide de Démarrage Rapide

Ce guide vous aidera à mettre en place et lancer la plateforme de monitoring et d'analyse de logs e-commerce.

## Prérequis

- **Docker** et **Docker Compose** installés
- **Python 3.9+** (pour le développement local)
- **Git** (pour cloner le projet)
- Au moins **8 GB RAM** disponible pour les conteneurs

## Installation

### Étape 1 : Configuration de l'environnement

1. Créer le fichier `.env` à partir du template :

```powershell
Copy-Item .env.example .env
```

2. Éditer le fichier `.env` et ajuster les paramètres selon vos besoins.

### Étape 2 : Lancer l'infrastructure avec Docker Compose

```powershell
# Démarrer tous les services
docker-compose up -d

# Vérifier que tous les conteneurs sont en cours d'exécution
docker-compose ps
```

Les services suivants seront démarrés :
- **Elasticsearch** : http://localhost:9200
- **Kibana** : http://localhost:5601
- **Logstash** : Port 5000 (TCP/UDP) et 5044 (Beats)
- **MongoDB** : Port 27017
- **Redis** : Port 6379
- **Flask App** : http://localhost:5000

### Étape 3 : Attendre que les services soient prêts

```powershell
# Vérifier Elasticsearch
Invoke-WebRequest -Uri http://localhost:9200 -Method GET

# Vérifier Kibana
Invoke-WebRequest -Uri http://localhost:5601 -Method GET

# Vérifier Flask
Invoke-WebRequest -Uri http://localhost:5000/health -Method GET
```

### Étape 4 : Initialiser Elasticsearch

```powershell
cd scripts
python setup_elasticsearch.py
```

### Étape 5 : Générer des logs de test (Optionnel)

```powershell
cd scripts
python generate_sample_logs.py -n 1000
```

## Développement Local (sans Docker)

### 1. Créer un environnement virtuel Python

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Installer les dépendances

```powershell
pip install -r requirements.txt
```

### 3. Lancer l'infrastructure (sans Flask)

Modifiez `docker-compose.yml` pour commenter le service `flask-app`, puis :

```powershell
docker-compose up -d
```

### 4. Lancer l'application Flask

```powershell
python main.py
```

## Utilisation

### Accéder aux interfaces

1. **Application Flask API**
   - URL : http://localhost:5000
   - Health check : http://localhost:5000/health

2. **Kibana Dashboard**
   - URL : http://localhost:5601
   - Pas d'authentification requise (dev mode)

3. **Elasticsearch**
   - URL : http://localhost:9200
   - Requête test : `http://localhost:9200/_cluster/health`

### Tester l'API

#### 1. Ingérer des logs

```powershell
$body = @{
    message = "Test transaction"
    log_type = "transaction"
    transaction_id = "TXN12345"
    user_id = "USER123"
    amount = 99.99
    currency = "USD"
    status = "completed"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/api/logs/ingest `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

#### 2. Récupérer les logs récents

```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/logs/recent?limit=10" `
    -Method GET
```

#### 3. Obtenir les statistiques

```powershell
Invoke-WebRequest -Uri http://localhost:5000/api/dashboard/overview `
    -Method GET
```

#### 4. Rechercher des logs

```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/search/?q=transaction&size=20" `
    -Method GET
```

### Uploader un fichier de logs

```powershell !
$filePath = "C:\chemin\vers\logs.json"
$formData = @{
    file = Get-Item -Path $filePath
}

Invoke-WebRequest -Uri http://localhost:5000/api/logs/upload `
    -Method POST `
    -Form $formData
```

## Tests

### Lancer les tests unitaires

```powershell
cd backend
pytest tests/ -v
```

### Avec couverture de code

```powershell
pytest tests/ --cov=app --cov-report=html
```

Les rapports de couverture seront générés dans `htmlcov/index.html`.

## Monitoring et Debugging

### Voir les logs des conteneurs

```powershell
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f elasticsearch
docker-compose logs -f flask-app
```

### Vérifier l'état des services

```powershell
docker-compose ps
```

### Accéder à un conteneur

```powershell
docker-compose exec flask-app bash
docker-compose exec elasticsearch bash
```

### Redémarrer un service

```powershell
docker-compose restart flask-app
```

## Arrêter les services

### Arrêt simple

```powershell
docker-compose stop
```

### Arrêt et suppression des conteneurs

```powershell
docker-compose down
```

### Arrêt et suppression des volumes (⚠️ supprime les données)

```powershell
docker-compose down -v
```

## Résolution de problèmes

### Problème : Elasticsearch ne démarre pas

**Solution** : Vérifier la mémoire disponible et les logs :

```powershell
docker-compose logs elasticsearch
```

Augmenter la mémoire dans `docker-compose.yml` si nécessaire.

### Problème : "Connection refused" vers Elasticsearch

**Solution** : Attendre que Elasticsearch soit complètement démarré (30-60 secondes).

### Problème : Port déjà utilisé

**Solution** : Vérifier les ports utilisés :

```powershell
netstat -ano | findstr :5000
netstat -ano | findstr :9200
```

Modifier les ports dans `docker-compose.yml` si nécessaire.

### Problème : Flask ne peut pas se connecter aux services

**Solution** : Vérifier que tous les services sont en cours d'exécution :

```powershell
docker-compose ps
```

Redémarrer si nécessaire :

```powershell
docker-compose restart
```

## Prochaines étapes

1. Consulter la [documentation de l'architecture](docs/architecture.md)
2. Lire la [documentation de l'API](docs/api_documentation.md)
3. Explorer les dashboards Kibana
4. Personnaliser les pipelines Logstash
5. Implémenter des alertes personnalisées

## Support

Pour toute question ou problème :
- Consulter la documentation dans `/docs`
- Vérifier les logs des services
- Ouvrir une issue sur le dépôt Git

## Ressources

- [Documentation Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Documentation Flask](https://flask.palletsprojects.com/)
- [Documentation Docker](https://docs.docker.com/)
- [Documentation MongoDB](https://docs.mongodb.com/)
