# JWT Authentication Implementation - Protected Routes

## Summary

Successfully added JWT authentication to protect sensitive routes in the Flask application.

## Protected Routes by Role

### Viewer Role (Minimum Access)
These routes require at least **viewer** role or higher:

#### Dashboard Routes
- `GET /dashboard` - Main dashboard HTML page
- `GET /api/dashboard/kpis` - Dashboard KPIs JSON
- `GET /api/dashboard/overview` - Dashboard overview data
- `GET /api/dashboard/metrics` - Key metrics
- `GET /api/dashboard/charts` - Chart data for visualizations

#### Search Routes
- `GET /api/search` - Search logs using Elasticsearch
- `GET /api/search/autocomplete` - Autocomplete suggestions

### Analyst Role (Data Analysis)
These routes require at least **analyst** role or higher:

#### Log Management
- `POST /api/logs/upload` - Upload log files (CSV or JSON)

#### Analytics Routes
- `GET /api/analytics/transactions` - Transaction analytics
- `GET /api/analytics/errors` - Error analytics
- `GET /api/analytics/user-behavior` - User behavior analytics

### Moderator Role
(Currently no specific moderator-only routes, but moderators have access to all analyst features)

### Admin Role
Admin routes are in the auth module:
- `GET /api/auth/users` - List all users
- `PUT /api/auth/users/<id>/role` - Update user role
- `POST /api/auth/users/<id>/deactivate` - Deactivate user
- `POST /api/auth/users/<id>/activate` - Activate user
- `DELETE /api/auth/users/<id>` - Delete user

## Public Routes (No Authentication Required)

- `GET /` - Home/welcome page
- `GET /health` - Health check endpoint
- `GET /kibana` - Kibana dashboard view (read-only)
- `GET /upload` - Upload page HTML (though posting requires auth)
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token

## How Authentication Works

### 1. Login to Get Token
```bash
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin12345"
}
```

Response includes `access_token` and `refresh_token`.

### 2. Use Token in Requests
Add the Authorization header to protected requests:
```bash
GET http://localhost:5000/dashboard
Authorization: Bearer <access_token>
```

### 3. Token Expiration
- **Access Token**: Expires in 1 hour
- **Refresh Token**: Expires in 30 days

Use the refresh endpoint to get a new access token without logging in again.

## Role Hierarchy

```
admin > moderator > analyst > viewer
```

- Users with **admin** role can access ALL routes
- Users with **analyst** role can access analytics AND viewer routes
- Users with **viewer** role can ONLY access viewer routes

## Testing Authentication

### Using curl (PowerShell)
```powershell
# Login
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
    -Method Post `
    -Body (@{username="admin"; password="admin12345"} | ConvertTo-Json) `
    -ContentType "application/json"

$token = $response.access_token

# Access protected route
$headers = @{Authorization="Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:5000/dashboard" -Headers $headers
```

### Using Python requests
```python
import requests

# Login
response = requests.post(
    "http://localhost:5000/api/auth/login",
    json={"username": "admin", "password": "admin12345"}
)
token = response.json()['access_token']

# Access protected route
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:5000/dashboard", headers=headers)
print(response.status_code)  # Should be 200
```

## Available Test Users

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| admin | admin12345 | admin | Full access |
| moderator_demo | moderator123 | moderator | Analyst + Viewer |
| analyst_demo | analyst123 | analyst | Analytics + Viewer |
| viewer_demo | viewer123 | viewer | Dashboard & Search only |

## Implementation Details

### Files Modified

1. **backend/app/routes/logs_routes.py**
   - Added JWT decorators to upload endpoint
   - Requires analyst role for file uploads

2. **backend/app/routes/dashboard_routes.py**
   - Protected all dashboard routes
   - Requires viewer role minimum

3. **backend/app/routes/analytics_routes.py**
   - Protected all analytics endpoints
   - Requires analyst role

4. **backend/app/routes/search_routes.py**
   - Protected search and autocomplete
   - Requires viewer role

### Decorators Used

- `@token_required` - Validates JWT token and injects current_user
- `@role_hierarchy_required('role')` - Checks if user has required role or higher

Example:
```python
from app.utils.jwt_utils import token_required, role_hierarchy_required

@bp.route('/analytics/transactions', methods=['GET'])
@token_required
@role_hierarchy_required('analyst')
def get_transaction_analytics():
    # current_user automatically available via decorator
    # Only accessible by analyst, moderator, or admin
    ...
```

## Error Responses

### 401 Unauthorized
No token provided or invalid token:
```json
{
  "error": "Authentication required",
  "message": "No token provided"
}
```

### 403 Forbidden
Valid token but insufficient role:
```json
{
  "error": "Access denied",
  "message": "Insufficient permissions. Required role: analyst or higher"
}
```

## Security Notes

✅ **Implemented:**
- JWT token validation on all sensitive routes
- Role-based access control with hierarchy
- Token expiration (1 hour access, 30 days refresh)
- Secure password hashing (bcrypt)

⚠️ **Production Recommendations:**
- Use HTTPS in production
- Store tokens securely (HTTP-only cookies for web apps)
- Implement rate limiting on login endpoint
- Add IP-based access controls for admin routes
- Enable CORS with proper origin restrictions
- Rotate JWT secret keys periodically
- Add request logging for security auditing

## Next Steps

1. **Test the protected routes** - Use test_protected_routes.py
2. **Add authentication to remaining routes** - Protect any other sensitive endpoints
3. **Implement refresh token rotation** - For enhanced security
4. **Add API rate limiting** - Prevent abuse
5. **Set up logging** - Track authentication attempts and access
6. **Deploy with HTTPS** - Essential for production

## Conclusion

✅ **All major routes are now protected with JWT authentication**

- Dashboard routes require viewer+ role
- Analytics routes require analyst+ role  
- Log upload requires analyst+ role
- Search requires viewer+ role
- Admin operations require admin role

The authentication system properly validates tokens and enforces role hierarchy, ensuring that only authorized users can access sensitive data and operations.
