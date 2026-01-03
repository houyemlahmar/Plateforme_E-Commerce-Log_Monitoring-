# JWT Authentication System - Quick Start

## 📋 Overview

A complete JWT authentication system has been implemented for your Flask application with the following features:

- ✅ User registration and login
- ✅ JWT token generation (access + refresh tokens)
- ✅ Token validation decorators
- ✅ Role-based access control (RBAC)
- ✅ Password hashing with bcrypt
- ✅ MongoDB user storage
- ✅ Role hierarchy system

## 🏗️ Architecture

### Files Created/Modified

```
backend/
├── app/
│   ├── models/
│   │   └── user_model.py          # User model and repository
│   ├── services/
│   │   └── auth_service.py        # Authentication logic
│   ├── utils/
│   │   └── jwt_utils.py           # JWT utilities and decorators
│   ├── routes/
│   │   └── auth_routes.py         # Authentication endpoints
│   └── __init__.py                # Updated to register auth blueprint
├── requirements.txt                # Updated with PyJWT
├── test_auth.py                   # Comprehensive test suite
├── init_admin.py                  # Admin user initialization script
└── JWT_AUTHENTICATION.md          # Complete documentation
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The following key packages are required:
- `PyJWT==2.8.0` - JWT token handling
- `bcrypt==4.1.2` - Password hashing (already installed)
- `pymongo==4.6.1` - MongoDB integration (already installed)

### 2. Ensure MongoDB is Running

Make sure MongoDB is accessible. Check your configuration in `.env`:

```bash
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=ecommerce_logs
MONGODB_USER=admin
MONGODB_PASSWORD=changeme
```

### 3. Create Admin User

```bash
python init_admin.py
```

This will:
- Create an initial admin user
- Optionally create sample users for testing
- Set up the user collection with proper indexes

### 4. Start the Application

```bash
python main.py
```

The application will start on `http://localhost:5000`

### 5. Test Authentication

```bash
# In another terminal
python test_auth.py
```

This runs a comprehensive test suite covering:
- User registration
- Login and token generation
- Protected endpoint access
- Role-based access control
- Token refresh
- Error handling

## 🔐 User Roles

The system implements a hierarchical role structure:

| Role | Level | Access |
|------|-------|--------|
| **admin** | 4 | Full system access |
| **moderator** | 3 | User management, content moderation |
| **analyst** | 2 | Data analysis, queries, reports |
| **viewer** | 1 | Read-only dashboard access |

## 🛠️ Using Authentication in Your Routes

### Simple Token Protection

```python
from app.utils.jwt_utils import token_required

@app.route('/api/logs')
@token_required
def get_logs(current_user):
    # current_user object is automatically provided
    return jsonify({
        'logs': [...],
        'accessed_by': current_user.username
    })
```

### Role-Based Protection

```python
from app.utils.jwt_utils import token_required, role_required

@app.route('/api/admin/settings')
@token_required
@role_required('admin')
def admin_settings(current_user):
    # Only accessible by users with 'admin' role
    return jsonify({'settings': {...}})
```

### Hierarchical Role Protection

```python
from app.utils.jwt_utils import token_required, role_hierarchy_required

@app.route('/api/analytics')
@token_required
@role_hierarchy_required('analyst')
def analytics(current_user):
    # Accessible by analyst, moderator, and admin
    return jsonify({'analytics': {...}})
```

## 📡 API Endpoints

### Public Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token

### Protected Endpoints (Require Token)

- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/me/password` - Change password

### Admin/Moderator Endpoints

- `GET /api/auth/users` - List all users (moderator+)
- `PUT /api/auth/users/<id>/role` - Update user role (admin)
- `POST /api/auth/users/<id>/activate` - Activate user (admin)
- `POST /api/auth/users/<id>/deactivate` - Deactivate user (admin)
- `DELETE /api/auth/users/<id>` - Delete user (admin)

## 🧪 Testing Examples

### cURL

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin12345"}'

# Access protected endpoint
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Python

```python
import requests

# Login
response = requests.post('http://localhost:5000/api/auth/login', 
    json={'username': 'admin', 'password': 'admin12345'})
token = response.json()['access_token']

# Access protected route
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:5000/api/auth/me', headers=headers)
print(response.json())
```

### JavaScript

```javascript
// Login
const response = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'admin12345'})
});
const {access_token} = await response.json();

// Access protected route
const userData = await fetch('http://localhost:5000/api/auth/me', {
  headers: {'Authorization': `Bearer ${access_token}`}
});
```

## 🔒 Security Features

✅ **Password Hashing**: bcrypt with automatic salting  
✅ **Token Expiration**: Access tokens expire after 1 hour  
✅ **Refresh Tokens**: 30-day validity for session extension  
✅ **Role Validation**: Automatic role checking on protected routes  
✅ **Active User Check**: Deactivated users cannot authenticate  
✅ **Token Type Verification**: Separate access and refresh tokens  

## ⚙️ Configuration

Add to your `.env` file:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour in seconds

# MongoDB (already configured)
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=ecommerce_logs
```

**⚠️ IMPORTANT**: Change `JWT_SECRET_KEY` in production!

```python
# Generate a secure key:
import secrets
print(secrets.token_hex(32))
```

## 📚 Documentation

For complete documentation, see [JWT_AUTHENTICATION.md](JWT_AUTHENTICATION.md)

Topics covered:
- Detailed API reference
- Authentication flow diagrams
- Security best practices
- Troubleshooting guide
- Migration guide for existing routes
- Database schema details

## 🎯 Next Steps

1. **Start the application**: `python main.py`
2. **Create admin user**: `python init_admin.py`
3. **Run tests**: `python test_auth.py`
4. **Protect existing routes**: Add decorators to your routes
5. **Customize roles**: Modify role definitions in `user_model.py`
6. **Update frontend**: Implement token storage and authentication

## 🔍 Protecting Existing Routes

To add authentication to your existing routes, simply add the decorators:

```python
# Before
@bp.route('/api/logs', methods=['GET'])
def get_logs():
    # ...existing code...
    pass

# After
@bp.route('/api/logs', methods=['GET'])
@token_required
@role_hierarchy_required('analyst')  # Requires analyst or higher
def get_logs(current_user):
    # ...existing code...
    logger.info(f"Logs accessed by {current_user.username}")
    pass
```

## 🐛 Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: Check with `docker ps` or service status
- Verify connection settings in `.env`

### Token Validation Fails
- Check `JWT_SECRET_KEY` is set correctly
- Ensure token format is `Bearer <token>` in Authorization header

### Import Errors
- Run `pip install -r requirements.txt` to ensure all dependencies are installed
- Verify virtual environment is activated

### User Creation Fails
- Check MongoDB database permissions
- Ensure unique username and email

## 📞 Support

For issues or questions:
1. Check [JWT_AUTHENTICATION.md](JWT_AUTHENTICATION.md) for detailed documentation
2. Review test examples in [test_auth.py](test_auth.py)
3. Check error logs in `app.log`

---

**Status**: ✅ Ready for use  
**Created**: January 2, 2026  
**Version**: 1.0.0
