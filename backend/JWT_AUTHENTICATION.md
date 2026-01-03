# JWT Authentication Implementation Guide

## Overview

This document describes the JWT authentication system implemented in the Flask application. The system provides secure user authentication, role-based access control, and token management using PyJWT and MongoDB.

## Architecture

### Components

1. **User Model** (`app/models/user_model.py`)
   - MongoDB-based user storage
   - User schema with roles and permissions
   - Repository pattern for database operations

2. **Authentication Service** (`app/services/auth_service.py`)
   - Password hashing with bcrypt
   - User registration and validation
   - User authentication and management

3. **JWT Utilities** (`app/utils/jwt_utils.py`)
   - Token generation and validation
   - Authentication decorators
   - Role-based access control decorators

4. **Authentication Routes** (`app/routes/auth_routes.py`)
   - RESTful API endpoints
   - Login, registration, token refresh
   - User management endpoints

## User Roles

The system supports a hierarchical role structure:

- **admin**: Full system access (highest privilege)
- **moderator**: Can manage users and moderate content
- **analyst**: Data analysis and query access
- **viewer**: Read-only access to dashboards (lowest privilege)

## API Endpoints

### Public Endpoints

#### POST `/api/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "username": "string (min 3 chars)",
  "email": "valid email address",
  "password": "string (min 8 chars)",
  "role": "viewer|analyst|moderator|admin (optional, default: viewer)"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "_id": "user_id",
    "username": "username",
    "email": "email",
    "role": "role",
    "is_active": true,
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
}
```

#### POST `/api/auth/login`
Authenticate and receive JWT tokens.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "Bearer",
  "user": {
    "_id": "user_id",
    "username": "username",
    "role": "role"
  }
}
```

#### POST `/api/auth/refresh`
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response (200):**
```json
{
  "message": "Token refreshed successfully",
  "access_token": "eyJhbGc...",
  "token_type": "Bearer"
}
```

### Protected Endpoints

All protected endpoints require the `Authorization` header:
```
Authorization: Bearer <access_token>
```

#### GET `/api/auth/me`
Get current user profile.

**Response (200):**
```json
{
  "user": {
    "_id": "user_id",
    "username": "username",
    "email": "email",
    "role": "role",
    "is_active": true,
    "last_login": "timestamp"
  }
}
```

#### PUT `/api/auth/me/password`
Change current user's password.

**Request Body:**
```json
{
  "old_password": "string",
  "new_password": "string (min 8 chars)"
}
```

#### GET `/api/auth/users` 
List all users (moderator/admin only).

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)

**Response (200):**
```json
{
  "users": [...],
  "total": 10,
  "skip": 0,
  "limit": 100
}
```

#### PUT `/api/auth/users/<user_id>/role`
Update user role (admin only).

**Request Body:**
```json
{
  "role": "admin|moderator|analyst|viewer"
}
```

#### POST `/api/auth/users/<user_id>/activate`
Activate user account (admin only).

#### POST `/api/auth/users/<user_id>/deactivate`
Deactivate user account (admin only).

#### DELETE `/api/auth/users/<user_id>`
Delete user (admin only).

## Using Authentication Decorators

### @token_required
Requires valid JWT token for access.

```python
from app.utils.jwt_utils import token_required

@app.route('/protected')
@token_required
def protected_route(current_user):
    return jsonify({
        'message': f'Hello {current_user.username}',
        'role': current_user.role
    })
```

### @role_required
Requires specific role(s). Must be used with `@token_required`.

```python
from app.utils.jwt_utils import token_required, role_required

@app.route('/admin-only')
@token_required
@role_required('admin')
def admin_route(current_user):
    return jsonify({'message': 'Admin access granted'})

@app.route('/analytics')
@token_required
@role_required('admin', 'analyst')
def analytics_route(current_user):
    # Accessible by admin OR analyst
    return jsonify({'message': 'Analytics access granted'})
```

### @role_hierarchy_required
Requires minimum role level (hierarchical).

```python
from app.utils.jwt_utils import token_required, role_hierarchy_required

@app.route('/analyst-area')
@token_required
@role_hierarchy_required('analyst')
def analyst_area(current_user):
    # Accessible by analyst, moderator, and admin
    return jsonify({'message': 'Analyst area'})
```

### @optional_token
Makes authentication optional. User info provided if token is valid.

```python
from app.utils.jwt_utils import optional_token

@app.route('/public-or-private')
@optional_token
def mixed_route(current_user):
    if current_user:
        return jsonify({'message': f'Hello {current_user.username}'})
    return jsonify({'message': 'Hello guest'})
```

## Token Structure

### Access Token
- **Purpose**: Authenticate API requests
- **Expiration**: 1 hour (configurable via `JWT_ACCESS_TOKEN_EXPIRES`)
- **Payload**:
  ```json
  {
    "user_id": "string",
    "username": "string",
    "role": "string",
    "type": "access",
    "iat": timestamp,
    "exp": timestamp
  }
  ```

### Refresh Token
- **Purpose**: Obtain new access tokens
- **Expiration**: 30 days
- **Payload**:
  ```json
  {
    "user_id": "string",
    "username": "string",
    "type": "refresh",
    "iat": timestamp,
    "exp": timestamp
  }
  ```

## Configuration

Add these variables to your `.env` file:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600  # seconds (1 hour)

# MongoDB Configuration (for user storage)
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=ecommerce_logs
MONGODB_USER=admin
MONGODB_PASSWORD=changeme
```

## Security Best Practices

1. **Secret Keys**: Use strong, random secret keys in production
   ```python
   # Generate a secure secret key:
   import secrets
   print(secrets.token_hex(32))
   ```

2. **HTTPS**: Always use HTTPS in production to prevent token interception

3. **Token Storage**: 
   - Store tokens securely on the client side
   - Use httpOnly cookies or secure storage mechanisms
   - Never store tokens in localStorage in production

4. **Password Requirements**:
   - Minimum 8 characters
   - Consider adding complexity requirements

5. **Rate Limiting**: Implement rate limiting on login endpoints

6. **Token Expiration**: 
   - Keep access token expiration short (1 hour)
   - Use refresh tokens for extended sessions

## Example Usage

### Python Client

```python
import requests

# 1. Register a new user
response = requests.post('http://localhost:5000/api/auth/register', json={
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'password123',
    'role': 'viewer'
})

# 2. Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'testuser',
    'password': 'password123'
})
data = response.json()
access_token = data['access_token']

# 3. Access protected endpoint
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get('http://localhost:5000/api/auth/me', headers=headers)
print(response.json())
```

### JavaScript Client

```javascript
// 1. Login
const loginResponse = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'testuser',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// 2. Access protected endpoint
const response = await fetch('http://localhost:5000/api/auth/me', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const userData = await response.json();
```

### cURL Examples

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Access protected endpoint
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Testing

Run the test suite:

```bash
# Start the Flask application
cd backend
python main.py

# In another terminal, run tests
python test_auth.py
```

## Troubleshooting

### Common Issues

1. **"Token has expired"**
   - Use the refresh token to get a new access token
   - Or login again

2. **"Invalid token"**
   - Check JWT_SECRET_KEY is consistent
   - Verify token format: `Bearer <token>`

3. **"User not found"**
   - Ensure MongoDB is running
   - Check database connection settings

4. **"Insufficient permissions"**
   - Verify user role in database
   - Check required role for endpoint

## Database Schema

### Users Collection

```javascript
{
  _id: ObjectId,
  username: String (unique),
  email: String (unique),
  password_hash: String,
  role: String (enum: ['admin', 'moderator', 'analyst', 'viewer']),
  is_active: Boolean,
  created_at: DateTime,
  updated_at: DateTime,
  last_login: DateTime
}
```

### Indexes

- `username`: Unique index
- `email`: Unique index  
- `role`: Regular index for query optimization

## Migration Guide

To add authentication to existing routes:

1. Import decorators:
   ```python
   from app.utils.jwt_utils import token_required, role_required
   ```

2. Add to route:
   ```python
   @app.route('/api/logs')
   @token_required
   @role_hierarchy_required('analyst')
   def get_logs(current_user):
       # Your existing code
       pass
   ```

3. Use `current_user` object:
   ```python
   logger.info(f"Logs accessed by {current_user.username}")
   ```

## Additional Resources

- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
