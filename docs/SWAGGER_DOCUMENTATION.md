# 📚 Swagger UI Documentation

## Vue d'ensemble

Swagger UI a été intégré à la plateforme pour fournir une documentation interactive de l'API.

## 🌐 Accès à Swagger UI

**URL** : http://localhost:5001/api/docs

## 📋 Endpoints Documentés

### 🔐 Authentication

#### POST /api/auth/login
- **Description** : Authentifier un utilisateur et générer des tokens JWT
- **Paramètres** :
  - `username` (string, required) - Email ou nom d'utilisateur
  - `password` (string, required) - Mot de passe
- **Réponses** :
  - `200` - Authentification réussie avec access_token et refresh_token
  - `400` - Identifiants manquants
  - `401` - Identifiants invalides
- **Exemple** :
```json
{
  "username": "admin@example.com",
  "password": "SecurePass123!"
}
```

### 📁 Logs Management

#### POST /api/logs/upload
- **Description** : Uploader un fichier de logs (CSV ou JSON)
- **Authentification** : Bearer token requis (Analyst+)
- **Paramètres** :
  - `file` (file, required) - Fichier de logs (max 100MB)
- **Formats acceptés** : CSV, JSON
- **Réponses** :
  - `201` - Fichier uploadé avec succès
  - `400` - Erreur de validation (format, taille)
  - `401` - Token manquant ou invalide
  - `403` - Permissions insuffisantes

#### POST /api/logs/search
- **Description** : Rechercher des logs avec filtres avancés
- **Authentification** : Non requise pour le moment
- **Paramètres** :
  - `query` (string, optional) - Recherche texte libre
  - `level` (string, optional) - Niveau de log (ERROR, WARNING, INFO, etc.)
  - `service` (string, optional) - Nom du service
  - `date_from` (string, optional) - Date de début (format: YYYY-MM-DD HH:MM)
  - `date_to` (string, optional) - Date de fin (format: YYYY-MM-DD HH:MM)
  - `size` (integer, optional) - Nombre de résultats (default: 100)
  - `from` (integer, optional) - Offset pour pagination (default: 0)
- **Réponses** :
  - `200` - Résultats de recherche avec hits, total, took (ms)
  - `400` - Paramètres invalides
  - `500` - Erreur serveur
- **Exemple** :
```json
{
  "query": "payment failed",
  "level": "ERROR",
  "service": "payment",
  "date_from": "2026-01-01 00:00",
  "date_to": "2026-01-03 23:59",
  "size": 50
}
```

#### GET /api/logs/{log_id}
- **Description** : Récupérer un log spécifique par son ID
- **Authentification** : Non requise pour le moment
- **Paramètres** :
  - `log_id` (path, required) - ID du document log
- **Réponses** :
  - `200` - Détails du log
  - `404` - Log non trouvé
  - `500` - Erreur serveur
- **Exemple** : `GET /api/logs/log_12345abc`

## 🔐 Utilisation de l'Authentification JWT

### Étape 1 : Obtenir un Token

1. Utilisez l'endpoint **POST /api/auth/login**
2. Fournissez vos identifiants :
```json
{
  "username": "admin@example.com",
  "password": "your_password"
}
```
3. Copiez le `access_token` de la réponse

### Étape 2 : Autoriser dans Swagger UI

1. Cliquez sur le bouton **"Authorize"** 🔒 en haut à droite de Swagger UI
2. Dans le champ "Value", entrez :
```
Bearer <votre_access_token>
```
Exemple :
```
Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiNjdhMWIy...
```
3. Cliquez sur **"Authorize"**
4. Fermez la fenêtre d'autorisation

### Étape 3 : Tester les Endpoints Protégés

Vous pouvez maintenant tester tous les endpoints qui nécessitent une authentification, comme :
- **POST /api/logs/upload**
- Tous les endpoints marqués avec un cadenas 🔒

## 📖 Fonctionnalités de Swagger UI

### Try it out
- Cliquez sur **"Try it out"** pour tester un endpoint directement
- Remplissez les paramètres requis
- Cliquez sur **"Execute"**
- Consultez la réponse avec le code de statut HTTP

### Schemas
- Consultez les modèles de données complets dans la section **"Schemas"**
- Voir les structures JSON attendues pour chaque endpoint

### Export
- Téléchargez la spécification OpenAPI JSON via :
  - http://localhost:5001/apispec.json

## 🛠️ Configuration Swagger

La configuration Swagger se trouve dans `backend/app/__init__.py` :

```python
swagger_config = {
    "headers": [],
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "E-Commerce Logs Platform API",
        "version": "2.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    }
}
```

## 📝 Ajouter de Nouveaux Endpoints

Pour documenter un nouvel endpoint, ajoutez un docstring YAML dans la fonction de route :

```python
@bp.route('/my-endpoint', methods=['POST'])
def my_endpoint():
    """
    Description de l'endpoint
    ---
    tags:
      - Category
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            param1:
              type: string
              example: "value"
    responses:
      200:
        description: Success response
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Success"
    """
    # Code de la route...
```

## 🎨 Tags Organisationnels

Les endpoints sont organisés par tags :
- **Authentication** - Endpoints d'authentification JWT
- **Logs** - Gestion des logs (upload, search, retrieve)
- **Analytics** - Métriques et analytics
- **Dashboard** - Endpoints pour dashboards

## 🔗 Liens Utiles

- **Swagger UI** : http://localhost:5001/api/docs
- **Spécification JSON** : http://localhost:5001/apispec.json
- **Documentation Flasgger** : https://github.com/flasgger/flasgger
- **OpenAPI 2.0 Spec** : https://swagger.io/specification/v2/

## 🐛 Troubleshooting

### Swagger UI ne charge pas
1. Vérifiez que Flask est démarré : `docker-compose logs flask-app`
2. Vérifiez l'installation de flasgger : `pip list | grep flasgger`
3. Redémarrez le conteneur : `docker-compose restart flask-app`

### Les endpoints ne s'affichent pas
1. Vérifiez le format YAML des docstrings
2. Consultez les logs Flask pour les erreurs de parsing
3. Validez la syntaxe OpenAPI

### L'authentification ne fonctionne pas
1. Assurez-vous d'avoir cliqué sur **"Authorize"**
2. Vérifiez le format : `Bearer <token>` (avec l'espace)
3. Vérifiez que le token n'est pas expiré (durée : 1 heure)

---

**Version** : 2.0.0 avec Swagger UI  
**Dernière mise à jour** : Janvier 2026
