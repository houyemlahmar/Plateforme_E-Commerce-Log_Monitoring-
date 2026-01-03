"""
JWT utilities for token generation and validation
Provides decorators for authentication and role-based access control
"""

import jwt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class JWTManager:
    """Manager for JWT token operations"""
    
    @staticmethod
    def generate_token(user_id, username, role, expires_in=None):
        """
        Generate a JWT access token
        
        Args:
            user_id: User ID
            username: Username
            role: User role
            expires_in: Token expiration time (timedelta or seconds)
        
        Returns:
            JWT token string
        """
        if expires_in is None:
            expires_in = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
        
        if isinstance(expires_in, int):
            expires_in = timedelta(seconds=expires_in)
        
        payload = {
            'user_id': str(user_id),
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + expires_in,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        secret_key = current_app.config.get('JWT_SECRET_KEY')
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        return token
    
    @staticmethod
    def generate_refresh_token(user_id, username):
        """
        Generate a JWT refresh token
        
        Args:
            user_id: User ID
            username: Username
        
        Returns:
            JWT refresh token string
        """
        payload = {
            'user_id': str(user_id),
            'username': username,
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        secret_key = current_app.config.get('JWT_SECRET_KEY')
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        return token
    
    @staticmethod
    def decode_token(token):
        """
        Decode and validate a JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Token payload dict
        
        Raises:
            jwt.ExpiredSignatureError: If token has expired
            jwt.InvalidTokenError: If token is invalid
        """
        secret_key = current_app.config.get('JWT_SECRET_KEY')
        
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise
    
    @staticmethod
    def get_token_from_header():
        """
        Extract JWT token from Authorization header
        
        Returns:
            Token string or None
        """
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        try:
            # Expected format: "Bearer <token>"
            parts = auth_header.split()
            
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return None
            
            return parts[1]
        except Exception as e:
            logger.error(f"Error extracting token from header: {str(e)}")
            return None


def token_required(f):
    """
    Decorator to require valid JWT token for route access
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({'message': 'Access granted'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from header
        token = JWTManager.get_token_from_header()
        
        if not token:
            return jsonify({
                'error': 'Authentication required',
                'message': 'No token provided'
            }), 401
        
        try:
            # Decode token
            payload = JWTManager.decode_token(token)
            
            # Verify token type
            if payload.get('type') != 'access':
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'Token type must be access'
                }), 401
            
            # Get user from database - use shared connection if available
            from flask import current_app
            from app.models.user_model import UserRepository
            
            try:
                # Try to use shared MongoDB connection from Flask app
                logger.info(f"Checking for shared MongoDB connection...")
                if hasattr(current_app, 'mongo_service') and current_app.mongo_service and current_app.mongo_service.client:
                    logger.info(f"Using shared MongoDB client")
                    user_repo = UserRepository(db_client=current_app.mongo_service.client)
                else:
                    # Fallback to creating new connection
                    logger.warning(f"No shared MongoDB connection, creating new one")
                    user_repo = UserRepository()
            except Exception as repo_error:
                logger.warning(f"Could not use shared MongoDB connection: {str(repo_error)}", exc_info=True)
                user_repo = UserRepository()
            
            logger.info(f"Looking up user by ID: {payload['user_id']}")
            user = user_repo.find_by_id(payload['user_id'])
            
            if not user:
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'User not found'
                }), 401
            
            if not user.is_active:
                return jsonify({
                    'error': 'Account inactive',
                    'message': 'User account has been deactivated'
                }), 401
            
            # Add user to kwargs
            return f(*args, current_user=user, **kwargs)
        
        except jwt.ExpiredSignatureError:
            return jsonify({
                'error': 'Token expired',
                'message': 'Your session has expired. Please login again'
            }), 401
        
        except jwt.InvalidTokenError:
            return jsonify({
                'error': 'Invalid token',
                'message': 'Token validation failed'
            }), 401
        
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Authentication failed',
                'message': 'An error occurred during authentication'
            }), 500
    
    return decorated


def role_required(*required_roles):
    """
    Decorator to require specific role(s) for route access
    Must be used after @token_required
    
    Usage:
        @app.route('/admin')
        @token_required
        @role_required('admin')
        def admin_route(current_user):
            return jsonify({'message': 'Admin access granted'})
        
        @app.route('/analytics')
        @token_required
        @role_required('admin', 'analyst')
        def analytics_route(current_user):
            return jsonify({'message': 'Analytics access granted'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get current_user from kwargs (set by token_required)
            current_user = kwargs.get('current_user')
            
            if not current_user:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'User not authenticated'
                }), 401
            
            # Check if user has any of the required roles
            if current_user.role not in required_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'This action requires one of the following roles: {", ".join(required_roles)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator


def role_hierarchy_required(minimum_role):
    """
    Decorator to require minimum role level based on hierarchy
    Role hierarchy: admin > moderator > analyst > viewer
    Must be used after @token_required
    
    Usage:
        @app.route('/analytics')
        @token_required
        @role_hierarchy_required('analyst')
        def analytics_route(current_user):
            # Accessible by analyst, moderator, and admin
            return jsonify({'message': 'Analytics access granted'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get current_user from kwargs (set by token_required)
            current_user = kwargs.get('current_user')
            
            if not current_user:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'User not authenticated'
                }), 401
            
            # Check role hierarchy
            if not current_user.has_role(minimum_role):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'This action requires {minimum_role} role or higher'
                }), 403
            
            # Remove current_user from kwargs if the wrapped function doesn't accept it
            # This allows functions to optionally receive current_user
            import inspect
            sig = inspect.signature(f)
            if 'current_user' in sig.parameters:
                # Function accepts current_user, pass it
                return f(*args, current_user=current_user, **kwargs)
            else:
                # Function doesn't accept current_user, remove it from kwargs
                filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'current_user'}
                return f(*args, **filtered_kwargs)
        
        return decorated
    
    return decorator


def optional_token(f):
    """
    Decorator that makes JWT token optional
    If token is provided and valid, current_user is set
    If token is not provided or invalid, current_user is None
    
    Usage:
        @app.route('/public-or-private')
        @optional_token
        def mixed_route(current_user):
            if current_user:
                return jsonify({'message': f'Hello {current_user.username}'})
            return jsonify({'message': 'Hello guest'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from header
        token = JWTManager.get_token_from_header()
        
        current_user = None
        
        if token:
            try:
                # Decode token
                payload = JWTManager.decode_token(token)
                
                # Verify token type
                if payload.get('type') == 'access':
                    # Get user from database
                    auth_service = AuthService()
                    user = auth_service.get_user_by_id(payload['user_id'])
                    
                    if user and user.is_active:
                        current_user = user
            
            except Exception as e:
                logger.debug(f"Optional token validation failed: {str(e)}")
                # Continue without user
        
        return f(*args, current_user=current_user, **kwargs)
    
    return decorated
