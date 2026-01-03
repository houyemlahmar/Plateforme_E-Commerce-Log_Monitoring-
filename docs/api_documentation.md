# Documentation API - Plateforme BigData E-Commerce

## Base URL

```
http://localhost:5001/api
```

## 🔐 Authentification

L'API utilise **JWT (JSON Web Tokens)** pour l'authentification. Tous les endpoints (sauf `/auth/login`, `/auth/register`, et `/health`) nécessitent un token d'accès valide.

### Obtenir un Token

```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"your_password"}'
```

**Réponse** :
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "67a1b2c3d4e5f6g7h8i9",
    "email": "user@example.com",
    "username": "johndoe",
    "role": "analyst"
  }
}
```

### Utiliser le Token

Incluez le token dans le header `Authorization` de chaque requête :

```bash
curl -X GET http://localhost:5001/api/dashboard/stats \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### Rafraîchir le Token

Les tokens d'accès expirent après **1 heure**. Utilisez le refresh token pour en obtenir un nouveau :

```bash
curl -X POST http://localhost:5001/api/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

### Rôles et Permissions

| Rôle | Permissions |
|------|-------------|
| **viewer** | Consultation dashboards, recherche basique |
| **analyst** | Viewer + upload logs, analytics, recherche avancée, export |
| **moderator** | Analyst + gestion utilisateurs CRUD |
| **admin** | Moderator + suppression utilisateurs, accès complet |

---

## 📋 Endpoints

### Health Check

#### GET /health

Vérifier si l'application est opérationnelle.

**Authentification** : Non requise

**Réponse** :

```json
{
  "status": "healthy",
  "service": "ecommerce-logs-platform",
  "version": "2.0.0"
}
```

---

## 🔐 Authentification

### POST /auth/register

Créer un nouveau compte utilisateur.

**Authentification** : Non requise

**Request Body** :

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "username": "johndoe",
  "role": "viewer"
}
```

**Validation** :
- `email` : Requis, format email valide, unique
- `password` : Requis, minimum 8 caractères
- `username` : Optionnel, alphanumérique
- `role` : Optionnel, défaut "viewer" (viewer|analyst|moderator|admin)

**Réponse** : `201 Created`

```json
{
  "access_token": "eyJ0eXAi...",
  "refresh_token": "eyJ0eXAi...",
  "user": {
    "id": "67a1b2c3d4e5f6g7h8i9",
    "email": "user@example.com",
    "username": "johndoe",
    "role": "viewer",
    "created_at": "2024-12-25T10:30:00Z"
  }
}
```

### POST /auth/login

Se connecter et obtenir des tokens JWT.

**Authentification** : Non requise

**Request Body** :

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Réponse** : `200 OK`

```json
{
  "access_token": "eyJ0eXAi...",
  "refresh_token": "eyJ0eXAi...",
  "user": {
    "id": "67a1b2c3d4e5f6g7h8i9",
    "email": "user@example.com",
    "username": "johndoe",
    "role": "analyst"
  }
}
```

**Erreurs** :
- `401 Unauthorized` : Email ou mot de passe incorrect
- `403 Forbidden` : Compte désactivé

### POST /auth/refresh

Rafraîchir le token d'accès expiré.

**Authentification** : Refresh token requis

**Headers** :
```
Authorization: Bearer YOUR_REFRESH_TOKEN
```

**Réponse** : `200 OK`

```json
{
  "access_token": "eyJ0eXAi..."
}
```

### POST /auth/logout

Déconnecter l'utilisateur (supprime les tokens côté client).

**Authentification** : Access token requis

**Réponse** : `200 OK`

```json
{
  "message": "Successfully logged out"
}
```

### GET /auth/me

Récupérer les informations de l'utilisateur connecté.

**Authentification** : Access token requis

**Réponse** : `200 OK`

```json
{
  "id": "67a1b2c3d4e5f6g7h8i9",
  "email": "user@example.com",
  "username": "johndoe",
  "role": "analyst",
  "is_active": true,
  "created_at": "2024-12-20T15:30:00Z",
  "last_login": "2024-12-25T10:30:00Z"
}
```

---

## 📁 Logs Management

### POST /logs/upload

Uploader un fichier de logs (JSON ou CSV).

**Authentification** : Analyst+ requis

**Request** :

- Content-Type: `multipart/form-data`
- Body: `file` (fichier de logs, max 100MB)

**Réponse** : `200 OK`

```json
{
  "message": "Logs uploaded successfully",
  "filename": "20251225_123456_abc123_test_logs.json",
  "records_processed": 1000,
  "file_id": "507f1f77bcf86cd799439011"
}
```

**Erreurs** :
- `400 Bad Request` : Fichier manquant, extension invalide, ou taille > 100MB
- `401 Unauthorized` : Token manquant ou invalide
- `403 Forbidden` : Rôle insuffisant (< Analyst)

### POST /logs/ingest

Ingérer des logs via payload JSON direct.

**Authentification** : Analyst+ requis

**Request Body** :

```json
{
  "message": "Transaction completed",
  "log_type": "transaction",
  "transaction_id": "TXN12345",
  "user_id": "USER123",
  "amount": 99.99,
  "currency": "USD",
  "level": "INFO",
  "service": "payment"
}
```

**Réponse** : `200 OK`

```json
{
  "message": "Logs ingested successfully",
  "records_processed": 1
}
```

#### GET /logs/types

Get available log types.

**Response**

```json
{
  "log_types": [
    {
      "id": "transaction",
      "name": "Transaction Logs",
      "description": "Payment, order, and refund logs"
    },
    ...
  ]
}
```

#### GET /logs/recent

Get recent logs.

**Query Parameters**

- `limit` (optional): Number of logs (default: 100)
- `log_type` (optional): Filter by type

**Response**

```json
{
  "logs": [...],
  "count": 100
}
```

#### GET /logs/stats

Get logs statistics.

**Response**

```json
{
  "total_files": 50,
  "log_types": [
    {"type": "transaction", "count": 1000},
    {"type": "error", "count": 50}
  ],
  "timeline": [...]
}
```

---

### Analytics

  "records_processed": 1,
  "indexed_at": "2024-12-25T10:30:00Z"
}
```

### GET /logs/types

Récupérer les types de logs disponibles.

**Authentification** : Viewer+ requis

**Réponse** : `200 OK`

```json
{
  "log_types": [
    {
      "id": "transaction",
      "name": "Transaction Logs",
      "description": "Payment, order, and refund logs"
    },
    {
      "id": "error",
      "name": "Error Logs",
      "description": "Application errors and exceptions"
    }
  ]
}
```

### GET /logs/recent

Récupérer les logs récents.

**Authentification** : Viewer+ requis

**Query Parameters** :
- `limit` (optionnel) : Nombre de logs (défaut: 100, max: 1000)
- `log_type` (optionnel) : Filtrer par type

**Réponse** : `200 OK`

```json
{
  "logs": [
    {
      "_id": "log_001",
      "message": "Transaction completed",
      "level": "INFO",
      "service": "payment",
      "timestamp": "2024-12-25T10:30:00Z"
    }
  ],
  "count": 100
}
```

### GET /logs/stats

Récupérer les statistiques globales des logs.

**Authentification** : Analyst+ requis

**Réponse** : `200 OK`

```json
{
  "total_files": 50,
  "total_logs": 50000,
  "log_types": [
    {"type": "transaction", "count": 40000},
    {"type": "error", "count": 5000},
    {"type": "info", "count": 5000}
  ],
  "timeline": [
    {"hour": "2024-12-25T10:00:00Z", "count": 1000}
  ]
}
```

---

## 🔍 Search & Analytics

### POST /logs/search

Rechercher des logs avec filtres avancés.

**Authentification** : Analyst+ requis

**Request Body** :

```json
{
  "query": "payment failed",
  "level": "ERROR",
  "service": "payment",
  "date_from": "2024-12-20 00:00",
  "date_to": "2024-12-25 23:59",
  "size": 50,
  "from": 0
}
```

**Paramètres** :
- `query` (optionnel) : Recherche texte libre sur tous les champs
- `level` (optionnel) : ERROR, WARNING, INFO, DEBUG, CRITICAL
- `service` (optionnel) : Nom du service (payment, auth, inventory, etc.)
- `date_from` (optionnel) : Date de début (format: YYYY-MM-DD HH:MM)
- `date_to` (optionnel) : Date de fin (format: YYYY-MM-DD HH:MM)
- `size` (optionnel) : Nombre de résultats (défaut: 50, max: 1000)
- `from` (optionnel) : Offset pour pagination (défaut: 0)

**Réponse** : `200 OK`

```json
{
  "hits": [
    {
      "_id": "log_001",
      "_score": 1.234,
      "_source": {
        "message": "Payment gateway timeout",
        "level": "ERROR",
        "service": "payment",
        "timestamp": "2024-12-25T10:30:00Z",
        "user_id": "USER123",
        "amount": 99.99
      }
    }
  ],
  "total": 150,
  "took": 23
}
```

### GET /logs/search/services

Lister tous les services ayant des logs indexés.

**Authentification** : Viewer+ requis

**Réponse** : `200 OK`

```json
{
  "services": [
    "payment",
    "auth",
    "inventory",
    "shipping",
    "notification"
  ]
}
```

### POST /logs/search/save

Sauvegarder une recherche pour un accès rapide ultérieur.

**Authentification** : Analyst+ requis

**Request Body** :

```json
{
  "name": "Erreurs Payment Hier",
  "filters": {
    "level": "ERROR",
    "service": "payment",
    "date_from": "2024-12-24 00:00",
    "date_to": "2024-12-24 23:59"
  }
}
```

**Réponse** : `201 Created`

```json
{
  "message": "Search saved successfully",
  "search_id": "507f1f77bcf86cd799439011",
  "name": "Erreurs Payment Hier"
}
```

### GET /logs/search/recent

Récupérer les recherches récentes de l'utilisateur.

**Authentification** : Analyst+ requis

**Query Parameters** :
- `limit` (optionnel) : Nombre de recherches (défaut: 5, max: 50)

**Réponse** : `200 OK`

```json
{
  "searches": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "Erreurs Payment Hier",
      "filters": {...},
      "created_at": "2024-12-25T10:30:00Z"
    }
  ],
  "count": 5
}
```

---

## 📊 Analytics & Dashboard

### GET /dashboard/stats

Récupérer les statistiques du dashboard (KPIs).

**Authentification** : Viewer+ requis

**Réponse** : `200 OK`

```json
{
  "total_logs": 50000,
  "error_rate": 5.2,
  "avg_response_time": 245,
  "active_services": 8,
  "growth_percentage": 12.5
}
```

### GET /analytics/logs-per-hour

Récupérer le nombre de logs par heure sur les dernières 24h.

**Authentification** : Analyst+ requis

**Réponse** : `200 OK`

```json
{
  "data": [
    {"hour": "2024-12-25T00:00:00Z", "count": 1000, "errors": 50},
    {"hour": "2024-12-25T01:00:00Z", "count": 950, "errors": 40}
  ]
}
```

### GET /analytics/top-countries

Récupérer le top 10 des pays par nombre de logs.

**Authentification** : Analyst+ requis

**Réponse** : `200 OK`

```json
{
  "countries": [
    {"country": "United States", "count": 15000},
    {"country": "France", "count": 8000},
    {"country": "Germany", "count": 5000}
  ]
}
```

### GET /analytics/top-products

Récupérer le top 10 des produits par volume de transactions.

**Authentification** : Analyst+ requis

**Réponse** : `200 OK`

```json
{
  "products": [
    {"product_id": "PROD001", "name": "Laptop", "count": 500, "revenue": 499500},
    {"product_id": "PROD002", "name": "Smartphone", "count": 800, "revenue": 399200}
  ]
}
```

### GET /analytics/transactions

Get transaction analytics.

**Authentification** : Analyst+ requis

**Query Parameters** :
- `start_date` (optionnel) : Date de début (format ISO: 2024-12-20T00:00:00Z)
- `end_date` (optionnel) : Date de fin (format ISO: 2024-12-25T23:59:59Z)
- `granularity` (optionnel) : hourly, daily, weekly, monthly (défaut: daily)

**Réponse** : `200 OK`

```json
{
  "timeline": [
    {"date": "2024-12-25", "count": 1000, "amount": 99900}
  ],
  "payment_methods": [
    {"method": "credit_card", "count": 600, "amount": 59940},
    {"method": "paypal", "count": 400, "amount": 39960}
  ],
  "transaction_status": [
    {"status": "completed", "count": 950},
    {"status": "failed", "count": 50}
  ]
}
```

---

## 👥 User Management

### GET /users

Lister tous les utilisateurs.

**Authentification** : Moderator+ requis

**Query Parameters** :
- `role` (optionnel) : Filtrer par rôle (viewer|analyst|moderator|admin)
- `is_active` (optionnel) : Filtrer par statut (true|false)
- `limit` (optionnel) : Nombre d'utilisateurs (défaut: 50, max: 200)
- `skip` (optionnel) : Offset pour pagination (défaut: 0)

**Réponse** : `200 OK`

```json
{
  "users": [
    {
      "id": "67a1b2c3d4e5f6g7h8i9",
      "email": "analyst@example.com",
      "username": "john_analyst",
      "role": "analyst",
      "is_active": true,
      "created_at": "2024-12-20T15:30:00Z",
      "last_login": "2024-12-25T10:30:00Z"
    }
  ],
  "total": 15,
  "count": 10
}
```

### GET /users/:user_id

Récupérer un utilisateur spécifique.

**Authentification** : Moderator+ requis

**Réponse** : `200 OK`

```json
{
  "id": "67a1b2c3d4e5f6g7h8i9",
  "email": "analyst@example.com",
  "username": "john_analyst",
  "role": "analyst",
  "is_active": true,
  "created_at": "2024-12-20T15:30:00Z",
  "last_login": "2024-12-25T10:30:00Z",
  "stats": {
    "uploads_count": 25,
    "searches_count": 150
  }
}
```

### PUT /users/:user_id

Modifier un utilisateur.

**Authentification** : Moderator+ requis

**Request Body** :

```json
{
  "role": "analyst",
  "is_active": true,
  "username": "new_username"
}
```

**Réponse** : `200 OK`

```json
{
  "message": "User updated successfully",
  "user": {
    "id": "67a1b2c3d4e5f6g7h8i9",
    "email": "analyst@example.com",
    "username": "new_username",
    "role": "analyst",
    "is_active": true
  }
}
```

**Erreurs** :
- `403 Forbidden` : Tentative de modification d'un utilisateur avec rôle supérieur
- `404 Not Found` : Utilisateur inexistant

### DELETE /users/:user_id

Supprimer un utilisateur (soft delete).

**Authentification** : Admin uniquement

**Réponse** : `200 OK`

```json
{
  "message": "User deleted successfully",
  "user_id": "67a1b2c3d4e5f6g7h8i9"
}
```

**Erreurs** :
- `403 Forbidden` : Seuls les Admins peuvent supprimer des utilisateurs
- `404 Not Found` : Utilisateur inexistant

---

## ❌ Codes d'Erreur

| Code | Description | Solution |
|------|-------------|----------|
| `400` | Bad Request | Vérifiez la syntaxe et les paramètres |
| `401` | Unauthorized | Token manquant, invalide ou expiré → reconnectez-vous |
| `403` | Forbidden | Permissions insuffisantes → vérifiez votre rôle |
| `404` | Not Found | Ressource inexistante |
| `409` | Conflict | Email déjà utilisé (inscription) |
| `413` | Payload Too Large | Fichier > 100MB |
| `422` | Unprocessable Entity | Validation échouée |
| `429` | Too Many Requests | Rate limit atteint → attendez 1 minute |
| `500` | Internal Server Error | Erreur serveur → contactez l'admin |

---

## 🔒 Sécurité

### Bonnes Pratiques

1. **Tokens** :
   - Ne partagez JAMAIS vos tokens
   - Stockez les tokens de manière sécurisée (localStorage, non accessible en JS externe)
   - Utilisez HTTPS en production

2. **Rate Limiting** :
   - Maximum 100 requêtes / minute par utilisateur
   - Maximum 10 tentatives de login échouées / 15 minutes

3. **Validation** :
   - Tous les inputs sont validés côté serveur
   - Sanitization automatique des noms de fichiers
   - Taille maximale des payloads JSON : 10MB

4. **CORS** :
   - Configuré pour `http://localhost:5001` uniquement
   - En production, configurez les origines autorisées dans `.env`

---

## 📖 Exemples Complets

### Workflow Complet : Upload et Recherche

```bash
# 1. Se connecter
TOKEN=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"password123"}' | jq -r '.access_token')

# 2. Uploader un fichier
curl -X POST http://localhost:5001/api/logs/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_logs.json"

# 3. Rechercher des erreurs payment
curl -X POST http://localhost:5001/api/logs/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "ERROR",
    "service": "payment",
    "date_from": "2024-12-24 00:00",
    "date_to": "2024-12-25 23:59"
  }' | jq

# 4. Sauvegarder la recherche
curl -X POST http://localhost:5001/api/logs/search/save \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Erreurs Payment Hier",
    "filters": {
      "level": "ERROR",
      "service": "payment"
    }
  }'
```

### Workflow Gestion Utilisateurs

```bash
# 1. Se connecter en tant qu'Admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin_pass"}' | jq -r '.access_token')

# 2. Lister tous les utilisateurs
curl -X GET http://localhost:5001/api/users \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# 3. Créer un nouvel utilisateur
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "username": "newuser",
    "role": "analyst"
  }' | jq

# 4. Modifier un utilisateur
curl -X PUT http://localhost:5001/api/users/67a1b2c3d4e5f6g7h8i9 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"moderator","is_active":true}' | jq

# 5. Désactiver un utilisateur
curl -X PUT http://localhost:5001/api/users/67a1b2c3d4e5f6g7h8i9 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active":false}' | jq
```

---

**Version API** : 2.0.0 (avec authentification JWT)  
**Documentation mise à jour** : Décembre 2024
```

#### GET /analytics/errors

Get error analytics.

**Response**

```json
{
  "error_codes": [...],
  "error_types": [...],
  "timeline": [...]
}
```

#### GET /analytics/user-behavior

Get user behavior analytics.

**Response**

```json
{
  "actions": [...],
  "pages": [...],
  "cart_abandonment_count": 150
}
```

#### GET /analytics/trends

Get trends analysis.

**Query Parameters**

- `time_range` (optional): 7d, 30d, etc. (default: 7d)

**Response**

```json
{
  "time_range": "7d",
  "log_types": [...]
}
```

---

### Dashboard

#### GET /dashboard/overview

Get dashboard overview.

**Response**

```json
{
  "total_logs_24h": 10000,
  "errors_24h": 150,
  "transactions_24h": 5000,
  "transaction_amount_24h": 250000.00,
  "fraud_alerts_24h": 5,
  "log_types_distribution": [...]
}
```

#### GET /dashboard/metrics

Get key metrics.

**Response**

```json
{
  "realtime": 1000,
  "last_24h": 10000,
  "last_7d": 50000,
  "error_rate": 1.5,
  "avg_response_time": 150.5
}
```

#### GET /dashboard/charts

Get chart data.

**Query Parameters**

- `chart_type`: transactions, errors, performance

**Response**

```json
{
  "labels": [...],
  "data": [...]
}
```

---

### Fraud Detection

#### POST /fraud/detect

Detect fraud in transaction data.

**Request**

```json
{
  "transaction_id": "TXN12345",
  "user_id": "USER123",
  "amount": 15000.00,
  "currency": "USD",
  "payment_method": "credit_card",
  "location": "XX"
}
```

**Response**

```json
{
  "is_fraud": true,
  "fraud_score": 85,
  "indicators": ["high_amount", "suspicious_location"],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET /fraud/suspicious-activities

Get suspicious activities.

**Query Parameters**

- `limit` (optional): Number of activities (default: 100)

**Response**

```json
{
  "activities": [...],
  "count": 25
}
```

#### GET /fraud/stats

Get fraud statistics.

**Response**

```json
{
  "total_fraud_detected_24h": 10,
  "avg_fraud_score": 65.5,
  "top_indicators": [...]
}
```

---

### Performance

#### GET /performance/metrics

Get performance metrics.

**Response**

```json
{
  "avg_response_time": 150.5,
  "max_response_time": 2500.0,
  "min_response_time": 10.0,
  "percentiles": {...},
  "by_endpoint": [...]
}
```

#### GET /performance/api-response-times

Get API response times.

**Response**

```json
{
  "timeline": [...],
  "by_api": [...]
}
```

#### GET /performance/database-latency

Get database latency.

**Response**

```json
{
  "avg_db_latency": 50.5,
  "max_db_latency": 500.0,
  "slow_queries_count": 10,
  "by_query_type": [...]
}
```

---

### Search

#### GET /search/

Search logs.

**Query Parameters**

- `q`: Search query
- `log_type` (optional): Filter by type
- `from` (optional): Start date
- `to` (optional): End date
- `size` (optional): Number of results (default: 100)

**Response**

```json
{
  "total": 1000,
  "results": [...],
  "query": "error",
  "filters": {...}
}
```

#### GET /search/autocomplete

Get autocomplete suggestions.

**Query Parameters**

- `q`: Partial query

**Response**

```json
{
  "suggestions": ["transaction", "transfer", "transmit"]
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "error": "Error message description"
}
```

### Status Codes

- `200` : Success
- `201` : Created
- `400` : Bad Request
- `404` : Not Found
- `500` : Internal Server Error
