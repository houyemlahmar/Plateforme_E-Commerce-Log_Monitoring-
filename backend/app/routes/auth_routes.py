"""
Authentication routes
Provides endpoints for user authentication and management
"""

import logging
from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.utils.jwt_utils import (
    JWTManager, 
    token_required, 
    role_required, 
    role_hierarchy_required,
    optional_token
)

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize auth service lazily
auth_service = None


def get_auth_service():
    """Get or create auth service instance"""
    global auth_service
    if auth_service is None:
        auth_service = AuthService()
    return auth_service


@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request Body:
        {
            "username": "string (required, min 3 chars)",
            "email": "string (required, valid email)",
            "password": "string (required, min 8 chars)",
            "role": "string (optional, default: viewer)"
        }
    
    Returns:
        201: User created successfully
        400: Validation error or user already exists
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body must be JSON'
            }), 400
        
        # Extract fields
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'viewer')
        
        # Validate required fields
        if not username or not email or not password:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'Username, email, and password are required'
            }), 400
        
        # Register user
        user = get_auth_service().register_user(username, email, password, role)
        
        logger.info(f"User registered successfully: {username}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({
            'error': 'Validation error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Registration failed',
            'message': 'An error occurred during registration'
        }), 500


@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and generate JWT tokens
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        description: User credentials
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: Username or email
              example: "admin@example.com"
            password:
              type: string
              description: User password
              example: "SecurePass123!"
    responses:
      200:
        description: Authentication successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Login successful"
            access_token:
              type: string
              description: JWT access token (valid for 1 hour)
              example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            refresh_token:
              type: string
              description: JWT refresh token (valid for 30 days)
              example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            user:
              type: object
              properties:
                id:
                  type: string
                  example: "67a1b2c3d4e5f6g7h8i9"
                username:
                  type: string
                  example: "admin@example.com"
                email:
                  type: string
                  example: "admin@example.com"
                role:
                  type: string
                  enum: [admin, moderator, analyst, viewer]
                  example: "admin"
                is_active:
                  type: boolean
                  example: true
                created_at:
                  type: string
                  example: "2026-01-01T10:00:00Z"
      400:
        description: Missing credentials
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing credentials"
            message:
              type: string
              example: "Username and password are required"
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid credentials"
            message:
              type: string
              example: "Username or password incorrect"
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body must be JSON'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'error': 'Missing credentials',
                'message': 'Username and password are required'
            }), 400
        
        # Authenticate user
        user = get_auth_service().authenticate_user(username, password)
        
        # Generate tokens
        access_token = JWTManager.generate_token(
            user._id, 
            user.username, 
            user.role
        )
        refresh_token = JWTManager.generate_refresh_token(
            user._id, 
            user.username
        )
        
        logger.info(f"User logged in: {username}")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'user': user.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Authentication failed',
            'message': str(e)
        }), 401
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Login failed',
            'message': 'An error occurred during login'
        }), 500


@bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh access token using refresh token
    
    Request Body:
        {
            "refresh_token": "string (required)"
        }
    
    Returns:
        200: New access token generated
        400: Missing refresh token
        401: Invalid or expired refresh token
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body must be JSON'
            }), 400
        
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({
                'error': 'Missing token',
                'message': 'Refresh token is required'
            }), 400
        
        # Decode refresh token
        payload = JWTManager.decode_token(refresh_token)
        
        # Verify token type
        if payload.get('type') != 'refresh':
            return jsonify({
                'error': 'Invalid token',
                'message': 'Token must be a refresh token'
            }), 401
        
        # Get user
        user = get_auth_service().get_user_by_id(payload['user_id'])
        
        if not user or not user.is_active:
            return jsonify({
                'error': 'Invalid token',
                'message': 'User not found or inactive'
            }), 401
        
        # Generate new access token
        new_access_token = JWTManager.generate_token(
            user._id,
            user.username,
            user.role
        )
        
        logger.info(f"Token refreshed for user: {user.username}")
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'access_token': new_access_token,
            'token_type': 'Bearer'
        }), 200
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({
            'error': 'Token refresh failed',
            'message': 'Invalid or expired refresh token'
        }), 401


@bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """
    Get current user profile
    
    Requires: Valid JWT token
    
    Returns:
        200: Current user information
        401: Unauthorized
    """
    return jsonify({
        'user': current_user.to_dict()
    }), 200


@bp.route('/me/password', methods=['PUT'])
@token_required
def change_password(current_user):
    """
    Change current user's password
    
    Requires: Valid JWT token
    
    Request Body:
        {
            "old_password": "string (required)",
            "new_password": "string (required)"
        }
    
    Returns:
        200: Password changed successfully
        400: Validation error
        401: Unauthorized
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body must be JSON'
            }), 400
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({
                'error': 'Missing fields',
                'message': 'Old password and new password are required'
            }), 400
        
        # Update password
        get_auth_service().update_user_password(
            current_user._id,
            old_password,
            new_password
        )
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Validation error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return jsonify({
            'error': 'Password change failed',
            'message': 'An error occurred while changing password'
        }), 500


@bp.route('/users', methods=['GET'])
@token_required
@role_hierarchy_required('moderator')
def list_users(current_user):
    """
    List all users (moderator and admin only)
    
    Requires: Valid JWT token with moderator or admin role
    
    Query Parameters:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records (default: 100)
    
    Returns:
        200: List of users
        403: Insufficient permissions
    """
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        users = get_auth_service().list_users(skip=skip, limit=limit)
        total = get_auth_service().user_repo.count()
        
        return jsonify({
            'users': users,
            'total': total,
            'skip': skip,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"List users error: {str(e)}")
        return jsonify({
            'error': 'Failed to list users',
            'message': 'An error occurred while retrieving users'
        }), 500


@bp.route('/users/<user_id>/role', methods=['PUT'])
@token_required
@role_required('admin')
def update_user_role(current_user, user_id):
    """
    Update user role (admin only)
    
    Requires: Valid JWT token with admin role
    
    Request Body:
        {
            "role": "string (required: admin, analyst, viewer, moderator)"
        }
    
    Returns:
        200: Role updated successfully
        400: Validation error
        403: Insufficient permissions
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body must be JSON'
            }), 400
        
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({
                'error': 'Missing field',
                'message': 'Role is required'
            }), 400
        
        # Update role
        updated_user = get_auth_service().update_user_role(user_id, new_role)
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': updated_user.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Validation error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Update role error: {str(e)}")
        return jsonify({
            'error': 'Role update failed',
            'message': 'An error occurred while updating role'
        }), 500


@bp.route('/users/<user_id>/deactivate', methods=['POST'])
@token_required
@role_required('admin')
def deactivate_user(current_user, user_id):
    """
    Deactivate user account (admin only)
    
    Requires: Valid JWT token with admin role
    
    Returns:
        200: User deactivated successfully
        403: Insufficient permissions
    """
    try:
        updated_user = get_auth_service().deactivate_user(user_id)
        
        return jsonify({
            'message': 'User deactivated successfully',
            'user': updated_user.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Deactivate user error: {str(e)}")
        return jsonify({
            'error': 'Deactivation failed',
            'message': 'An error occurred while deactivating user'
        }), 500


@bp.route('/users/<user_id>/activate', methods=['POST'])
@token_required
@role_required('admin')
def activate_user(current_user, user_id):
    """
    Activate user account (admin only)
    
    Requires: Valid JWT token with admin role
    
    Returns:
        200: User activated successfully
        403: Insufficient permissions
    """
    try:
        updated_user = get_auth_service().activate_user(user_id)
        
        return jsonify({
            'message': 'User activated successfully',
            'user': updated_user.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Activate user error: {str(e)}")
        return jsonify({
            'error': 'Activation failed',
            'message': 'An error occurred while activating user'
        }), 500


@bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_user(current_user, user_id):
    """
    Delete user (admin only)
    
    Requires: Valid JWT token with admin role
    
    Returns:
        200: User deleted successfully
        403: Insufficient permissions
    """
    try:
        # Prevent self-deletion
        if str(current_user._id) == user_id:
            return jsonify({
                'error': 'Invalid operation',
                'message': 'Cannot delete your own account'
            }), 400
        
        deleted = get_auth_service().delete_user(user_id)
        
        if not deleted:
            return jsonify({
                'error': 'Not found',
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'message': 'User deleted successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Delete user error: {str(e)}")
        return jsonify({
            'error': 'Deletion failed',
            'message': 'An error occurred while deleting user'
        }), 500


# Example protected routes demonstrating role-based access

@bp.route('/admin-only', methods=['GET'])
@token_required
@role_required('admin')
def admin_only_route(current_user):
    """
    Example admin-only route
    
    Requires: Valid JWT token with admin role
    """
    return jsonify({
        'message': 'Welcome to the admin area',
        'user': current_user.username,
        'role': current_user.role
    }), 200


@bp.route('/analyst-area', methods=['GET'])
@token_required
@role_hierarchy_required('analyst')
def analyst_area_route(current_user):
    """
    Example analyst area route
    Accessible by analyst, moderator, and admin
    
    Requires: Valid JWT token with analyst role or higher
    """
    return jsonify({
        'message': 'Welcome to the analyst area',
        'user': current_user.username,
        'role': current_user.role
    }), 200


@bp.route('/public-or-private', methods=['GET'])
@optional_token
def public_or_private_route(current_user):
    """
    Example route with optional authentication
    Works with or without token
    """
    if current_user:
        return jsonify({
            'message': f'Hello {current_user.username}!',
            'authenticated': True,
            'role': current_user.role
        }), 200
    
    return jsonify({
        'message': 'Hello guest!',
        'authenticated': False
    }), 200
