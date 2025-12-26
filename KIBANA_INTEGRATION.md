# Kibana Integration - Embedded Dashboard

## Vue d'ensemble

La route `/kibana` permet d'afficher le dashboard Kibana directement dans l'interface Flask, sans avoir à ouvrir Kibana dans un onglet séparé.

## Accès

**URL:** http://localhost:5000/kibana

Le dashboard est accessible depuis le menu de navigation principal sous l'onglet "Kibana".

## Fonctionnalités

### 1. Iframe Intégré
- Le dashboard Kibana est embarqué dans un iframe responsive
- Design cohérent avec le reste de l'application
- Écran de chargement avec animation pendant l'initialisation

### 2. Contrôles Interactifs
- **Bouton Rafraîchir:** Recharge l'iframe pour mettre à jour les données
- **Bouton "Ouvrir dans Kibana":** Ouvre le dashboard dans un nouvel onglet pour une vue pleine page

### 3. Gestion des Erreurs
- Détection automatique si Kibana n'est pas accessible
- Message d'erreur informatif en cas de problème de connexion
- Timeout de chargement après 10 secondes

## Configuration Technique

### Headers de Sécurité

La configuration a été ajustée pour permettre l'embedding en iframe :

**kibana.yml:**
```yaml
# Allow embedding in iframes
server.customResponseHeaders:
  X-Frame-Options: "ALLOWALL"

# CORS configuration
server.cors.enabled: true
server.cors.allowOrigin: ["http://localhost:5000", "http://127.0.0.1:5000"]
server.cors.allowCredentials: true
```

### Attributs Sandbox de l'Iframe

L'iframe utilise les attributs suivants pour la sécurité :
```html
sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
```

Permissions accordées :
- `allow-same-origin`: Permet l'accès aux ressources du même domaine
- `allow-scripts`: Autorise l'exécution de JavaScript (nécessaire pour Kibana)
- `allow-popups`: Permet les popups (pour les exports, etc.)
- `allow-forms`: Autorise la soumission de formulaires

## Dashboard Embarqué

Le dashboard `ecommerce-logs-dashboard` contient 3 visualisations :

### 1. Logs par Heure (Haut - Pleine Largeur)
- **Type:** Line chart
- **Données:** Nombre de logs et erreurs sur 24h
- **Agrégation:** Date histogram (1h)

### 2. Top Messages d'Erreur (Bas Gauche)
- **Type:** Horizontal bar chart
- **Données:** Top 10 des messages d'erreur par service
- **Filtres:** ERROR et CRITICAL uniquement

### 3. Distribution des Montants (Bas Droite)
- **Type:** Donut chart
- **Données:** Répartition des montants de transactions
- **Ranges:** 0-50€, 50-100€, 100-200€, 200-500€, 500-1000€, 1000€+

## Architecture du Code

### Route Flask
**Fichier:** `backend/app/routes/dashboard_routes.py`

```python
@dashboard_view_bp.route('/kibana', methods=['GET'])
def kibana_view():
    """Render Kibana dashboard embedded in iframe"""
    config = get_config()
    kibana_url = config.KIBANA_URL if hasattr(config, 'KIBANA_URL') else 'http://localhost:5601'
    dashboard_id = 'ecommerce-logs-dashboard'
    kibana_dashboard_url = f"{kibana_url}/app/dashboards#/view/{dashboard_id}"
    
    return render_template('kibana.html', kibana_url=kibana_dashboard_url)
```

### Template HTML
**Fichier:** `backend/app/templates/kibana.html`

- Étend `base.html` pour la cohérence UI
- Overlay de chargement avec spinner
- Gestion d'erreurs JavaScript
- Style responsive avec Tailwind CSS

## Dépannage

### Le Dashboard ne se Charge Pas

1. **Vérifier que Kibana est démarré:**
   ```powershell
   docker ps | Select-String kibana
   ```

2. **Vérifier la configuration CORS:**
   ```powershell
   docker exec kibana cat /usr/share/kibana/config/kibana.yml | Select-String cors
   ```

3. **Redémarrer Kibana:**
   ```powershell
   docker restart kibana
   ```

4. **Vérifier les logs Kibana:**
   ```powershell
   docker logs kibana --tail 50
   ```

### Erreur X-Frame-Options

Si vous voyez une erreur "Refused to display in a frame", vérifiez :

1. `X-Frame-Options` dans kibana.yml est défini sur `ALLOWALL`
2. Kibana a été redémarré après modification
3. Le cache du navigateur a été vidé

### CORS Errors

Si vous voyez des erreurs CORS dans la console :

1. Ajoutez l'origine de votre app Flask dans `server.cors.allowOrigin`
2. Vérifiez que `server.cors.enabled: true`
3. Redémarrez Kibana

## Sécurité

### Considérations Importantes

1. **X-Frame-Options: ALLOWALL**
   - Nécessaire pour l'embedding
   - À utiliser uniquement en développement ou réseau interne
   - En production, limiter avec `server.cors.allowOrigin` spécifiques

2. **CORS Configuration**
   - Liste blanche des origines autorisées
   - Éviter `*` en production
   - Utiliser HTTPS en production

3. **Sandbox Attributes**
   - Minimiser les permissions de l'iframe
   - Ne pas ajouter `allow-top-navigation` (risque de détournement)

### Recommandations Production

Pour un déploiement en production :

```yaml
# kibana.yml - Production
server.customResponseHeaders:
  X-Frame-Options: "SAMEORIGIN"  # Plus restrictif

server.cors.allowOrigin: ["https://votredomaine.com"]  # Domaine spécifique
server.cors.allowCredentials: true

xpack.security.enabled: true  # Activer la sécurité
```

## Performance

### Optimisations

1. **Lazy Loading:** L'iframe ne charge que lorsque la page /kibana est visitée
2. **Timeout Management:** Détection automatique si Kibana ne répond pas
3. **Cache Headers:** Utiliser les headers de cache pour les ressources statiques

### Monitoring

Surveillez :
- Temps de chargement de l'iframe
- Taux d'erreur de connexion
- Performance du dashboard Kibana

## Maintenance

### Mise à Jour du Dashboard

Pour modifier le dashboard embarqué :

1. Modifiez `ecommerce_dashboard.ndjson`
2. Re-importez avec l'API Kibana :
   ```powershell
   docker cp kibana_exports/ecommerce_dashboard.ndjson kibana:/tmp/
   docker exec kibana curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" -H "kbn-xsrf: true" -F "file=@/tmp/ecommerce_dashboard.ndjson"
   ```

3. Rafraîchissez la page /kibana

### Changer l'URL Kibana

Modifiez dans `backend/config.py` :
```python
KIBANA_URL = 'http://votre-kibana:5601'
```

## Support

Pour les problèmes liés à :
- **Kibana:** Consultez [Elastic Documentation](https://www.elastic.co/guide/en/kibana/8.11/index.html)
- **Flask:** Vérifiez les logs Flask : `docker logs backend`
- **Integration:** Ouvrez la console développeur du navigateur (F12)
