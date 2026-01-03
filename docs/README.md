# 📚 Documentation du Projet

Ce dossier contient toute la documentation technique du projet BigData E-Commerce.

## 📖 Guides Principaux

### Documentation Essentielle
- **[README.md](../README.md)** - Documentation principale avec guide complet JWT (à la racine)
- **[api_documentation.md](api_documentation.md)** - Documentation complète des endpoints API avec exemples curl authentifiés
- **[architecture.md](architecture.md)** - Architecture technique du système
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Résumé complet du projet avec métriques

### Guides de Démarrage
- **[quick_start.md](quick_start.md)** - Guide de démarrage rapide (installation et premiers pas)

### Guides d'Intégration
- **[KIBANA_INTEGRATION.md](KIBANA_INTEGRATION.md)** - Guide complet pour intégrer Kibana avec iframe
- **[SEARCH_IMPLEMENTATION.md](SEARCH_IMPLEMENTATION.md)** - Implémentation de la recherche avancée
- **[UPLOAD_ENDPOINT_IMPLEMENTATION.md](UPLOAD_ENDPOINT_IMPLEMENTATION.md)** - Implémentation de l'endpoint d'upload

### Guides Docker
- **[ARCHITECTURE_DOCKER.md](ARCHITECTURE_DOCKER.md)** - Architecture Docker détaillée des 8 services
- **[DOCKER_INGESTION_GUIDE.md](DOCKER_INGESTION_GUIDE.md)** - Guide d'ingestion de logs avec Docker
- **[INGESTION_SERVICE.md](INGESTION_SERVICE.md)** - Service d'ingestion et traitement asynchrone

---

## 🗂️ Organisation

```
docs/
├── README.md (ce fichier)
├── api_documentation.md          # 🔐 25+ endpoints avec authentification JWT
├── architecture.md               # Stack technique et architecture microservices
├── quick_start.md                # Installation Docker et premiers pas
├── PROJECT_SUMMARY.md            # Vue d'ensemble complète (520+ lignes)
├── KIBANA_INTEGRATION.md         # Embedding Kibana avec CORS
├── SEARCH_IMPLEMENTATION.md      # Elasticsearch + filtres avancés
├── UPLOAD_ENDPOINT_IMPLEMENTATION.md # Upload JSON/CSV max 100MB
├── ARCHITECTURE_DOCKER.md        # 8 services orchestrés
├── DOCKER_INGESTION_GUIDE.md     # Logstash pipelines JSON/CSV
└── INGESTION_SERVICE.md          # Celery workers + Redis queue
```

---

## 🎯 Par Cas d'Usage

### Je veux démarrer le projet
1. Lire **[quick_start.md](quick_start.md)** pour l'installation
2. Consulter **[README.md](../README.md)** section "Démarrage Rapide"
3. Créer un compte admin via `/login`

### Je veux développer avec l'API
1. Lire **[api_documentation.md](api_documentation.md)** pour tous les endpoints
2. Section "Authentification" pour obtenir un token JWT
3. Exemples curl pour chaque endpoint

### Je veux comprendre l'architecture
1. Lire **[architecture.md](architecture.md)** pour la stack technique
2. Consulter **[ARCHITECTURE_DOCKER.md](ARCHITECTURE_DOCKER.md)** pour les services
3. Voir **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** pour la vue d'ensemble

### Je veux intégrer Kibana
1. Suivre **[KIBANA_INTEGRATION.md](KIBANA_INTEGRATION.md)** pas à pas
2. Configuration CORS et X-Frame-Options
3. Import des visualisations via API

### Je veux implémenter la recherche
1. Lire **[SEARCH_IMPLEMENTATION.md](SEARCH_IMPLEMENTATION.md)**
2. Filtres avancés, sauvegarde, cache Redis
3. Exemples de requêtes Elasticsearch

### Je veux uploader des logs
1. Consulter **[UPLOAD_ENDPOINT_IMPLEMENTATION.md](UPLOAD_ENDPOINT_IMPLEMENTATION.md)**
2. Formats JSON/CSV acceptés
3. Validation et traitement asynchrone

---

## 🔐 Sécurité

Toute la documentation reflète l'authentification JWT :
- **Rôles** : admin, moderator, analyst, viewer
- **Tokens** : access (1h) et refresh (30j)
- **Permissions** : Chaque endpoint indique le rôle minimum requis

---

## 📝 Contribuer à la Documentation

Pour améliorer la documentation :
1. Mettre à jour le fichier concerné dans `docs/`
2. Vérifier la cohérence avec `README.md` (racine)
3. Tester les exemples curl fournis
4. Mettre à jour les numéros de version si nécessaire

---

**Version Documentation** : 2.0.0 (avec JWT)  
**Dernière mise à jour** : Janvier 2026
