# 🧪 Tests Unitaires

Ce dossier contient tous les tests unitaires et d'intégration du projet BigData E-Commerce.

## 📋 Organisation des Tests

### Tests par Composant

#### **test_auth.py** 🔐
Tests d'authentification JWT :
- Inscription utilisateur
- Login et génération tokens
- Refresh token
- Validation token expiré
- Permissions par rôle

#### **test_routes.py**
Tests des routes API :
- Endpoints logs (upload, search, stats)
- Endpoints analytics
- Endpoints dashboard
- Validation des réponses

#### **test_models.py**
Tests des modèles de données :
- User model (création, validation, rôles)
- Log model
- Transaction model
- Validation des champs

#### **test_utils.py**
Tests des utilitaires :
- Decorators JWT (@token_required, @role_required)
- Validators (email, fichiers, etc.)
- Formatters
- Helpers

#### **test_query_builder.py**
Tests du constructeur de requêtes Elasticsearch :
- Queries simples et complexes
- Filtres multiples
- Agrégations
- Tri et pagination

#### **test_query_builder_api.py**
Tests de l'API query builder :
- Endpoint /api/logs/search
- Filtres avancés (level, service, date)
- Validation des paramètres
- Réponses JSON

#### **test_search_cache_history.py**
Tests recherche, cache et historique :
- Cache Redis pour recherches fréquentes
- Sauvegarde des recherches
- Historique utilisateur
- TTL et invalidation cache

#### **test_upload_endpoint.py**
Tests de l'endpoint d'upload :
- Upload JSON valide
- Upload CSV valide
- Validation taille (max 100MB)
- Validation extension
- Erreurs de format

#### **benchmark.py**
Tests de performance :
- Throughput upload (KB/s)
- Latence API (ms)
- Temps d'indexation Elasticsearch
- Charge CPU/Mémoire

---

## 🚀 Exécuter les Tests

### Tous les Tests
```powershell
cd C:\projet_bigdata\backend
pytest tests/ -v
```

### Tests Spécifiques
```powershell
# Tests authentification uniquement
pytest tests/test_auth.py -v

# Tests upload uniquement
pytest tests/test_upload_endpoint.py -v

# Tests avec couverture
pytest tests/ --cov=app --cov-report=html
```

### Tests par Catégorie
```powershell
# Tests unitaires (rapides)
pytest tests/test_models.py tests/test_utils.py -v

# Tests d'intégration (avec services externes)
pytest tests/test_routes.py tests/test_upload_endpoint.py -v

# Tests de performance
python tests/benchmark.py
```

---

## 📊 Couverture de Code

Objectif : **90%+ de couverture**

### Générer le Rapport
```powershell
pytest tests/ --cov=app --cov-report=term --cov-report=html
# Ouvrir htmlcov/index.html dans le navigateur
```

### Couverture Actuelle (estimée)
- **Models** : 85%
- **Routes** : 80%
- **Services** : 75%
- **Utils** : 90%
- **Auth** : 95%

---

## 🛠️ Configuration

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### conftest.py
Fixtures partagées :
- `client` : Client Flask de test
- `auth_headers` : Headers avec token JWT valide
- `mock_elasticsearch` : Mock Elasticsearch pour tests unitaires
- `mock_mongodb` : Mock MongoDB pour tests unitaires

---

## ✅ Checklist avant Commit

- [ ] Tous les tests passent (`pytest tests/ -v`)
- [ ] Couverture > 80% (`pytest --cov`)
- [ ] Pas de warnings
- [ ] Tests ajoutés pour les nouvelles fonctionnalités
- [ ] Tests d'authentification si endpoint protégé

---

## 🐛 Debugging Tests

### Afficher les Logs
```powershell
pytest tests/test_routes.py -v -s
```

### Arrêter au Premier Échec
```powershell
pytest tests/ -x
```

### Exécuter un Test Spécifique
```powershell
pytest tests/test_auth.py::test_login_success -v
```

### Mode Debug
```powershell
pytest tests/test_auth.py --pdb
```

---

## 📝 Ajouter un Nouveau Test

### Template
```python
import pytest
from flask import json

def test_nom_descriptif(client, auth_headers):
    """
    Test la fonctionnalité X.
    
    Vérifie que :
    - Condition 1
    - Condition 2
    """
    # Arrange
    data = {"key": "value"}
    
    # Act
    response = client.post(
        '/api/endpoint',
        headers=auth_headers,
        data=json.dumps(data),
        content_type='application/json'
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json['key'] == 'expected_value'
```

---

## 🎯 Tests à Ajouter (TODO)

- [ ] Tests de charge (Locust)
- [ ] Tests de sécurité JWT (tokens falsifiés)
- [ ] Tests de concurrence (upload simultanés)
- [ ] Tests E2E avec Selenium
- [ ] Tests de migration de données

---

**Couverture actuelle** : ~82%  
**Objectif** : 90%+  
**Tests totaux** : 50+  
**Dernière mise à jour** : Janvier 2026
