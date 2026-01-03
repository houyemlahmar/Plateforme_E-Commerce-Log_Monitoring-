"""
Example: Protecting Existing Routes with JWT Authentication

This file demonstrates how to add authentication to your existing Flask routes.
"""

from flask import Blueprint, jsonify
from app.utils.jwt_utils import (
    token_required, 
    role_required, 
    role_hierarchy_required,
    optional_token
)

# Example: Protecting logs endpoints
bp_logs_example = Blueprint('logs_protected', __name__, url_prefix='/api/logs')


# Example 1: Basic Token Protection
# Anyone with a valid token can access
@bp_logs_example.route('/upload', methods=['POST'])
@token_required
def upload_logs(current_user):
    """
    Upload logs endpoint - requires authentication
    Any authenticated user can upload logs
    """
    return jsonify({
        'message': f'Logs uploaded by {current_user.username}',
        'uploaded_by': current_user.username,
        'role': current_user.role
    })


# Example 2: Role-Based Access
# Only admin and moderator can access
@bp_logs_example.route('/delete/<log_id>', methods=['DELETE'])
@token_required
@role_required('admin', 'moderator')
def delete_log(current_user, log_id):
    """
    Delete log endpoint - admin or moderator only
    """
    return jsonify({
        'message': f'Log {log_id} deleted by {current_user.username}',
        'deleted_by': current_user.username,
        'role': current_user.role
    })


# Example 3: Hierarchical Role Access
# Analyst and above (analyst, moderator, admin) can access
@bp_logs_example.route('/analytics', methods=['GET'])
@token_required
@role_hierarchy_required('analyst')
def log_analytics(current_user):
    """
    Log analytics endpoint - analyst or higher
    Accessible by: analyst, moderator, admin
    """
    return jsonify({
        'message': 'Analytics data',
        'accessed_by': current_user.username,
        'role': current_user.role,
        'analytics': {
            'total_logs': 1000,
            'errors': 50,
            'warnings': 200
        }
    })


# Example 4: Optional Authentication
# Works with or without authentication
@bp_logs_example.route('/public-stats', methods=['GET'])
@optional_token
def public_stats(current_user):
    """
    Public statistics - authentication optional
    If authenticated, shows personalized data
    """
    stats = {
        'total_logs': 1000,
        'uptime': '99.9%'
    }
    
    if current_user:
        # Add personalized data for authenticated users
        stats['user'] = current_user.username
        stats['your_logs'] = 25
        stats['personalized'] = True
    else:
        stats['personalized'] = False
    
    return jsonify(stats)


# Example 5: Admin-Only Endpoint
@bp_logs_example.route('/admin/purge', methods=['POST'])
@token_required
@role_required('admin')
def purge_logs(current_user):
    """
    Purge all logs - admin only
    """
    return jsonify({
        'message': 'All logs purged',
        'purged_by': current_user.username,
        'role': current_user.role
    })


# Example 6: Using current_user Object
@bp_logs_example.route('/my-logs', methods=['GET'])
@token_required
def get_my_logs(current_user):
    """
    Get logs for the current authenticated user
    Demonstrates using current_user object properties
    """
    # Access user properties
    user_info = {
        'id': str(current_user._id),
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role,
        'is_active': current_user.is_active,
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
        'last_login': current_user.last_login.isoformat() if current_user.last_login else None
    }
    
    # Use role checking method
    can_delete = current_user.has_role('moderator')
    can_analyze = current_user.has_role('analyst')
    
    return jsonify({
        'user': user_info,
        'permissions': {
            'can_delete': can_delete,
            'can_analyze': can_analyze
        },
        'logs': [
            # Your logs query filtered by user
        ]
    })


# Example 7: Conditional Logic Based on Role
@bp_logs_example.route('/view/<log_id>', methods=['GET'])
@token_required
def view_log(current_user, log_id):
    """
    View log with different detail levels based on role
    """
    # Basic log data available to everyone
    log_data = {
        'id': log_id,
        'timestamp': '2026-01-02T10:00:00Z',
        'level': 'INFO',
        'message': 'User login'
    }
    
    # Add sensitive data for analysts and above
    if current_user.has_role('analyst'):
        log_data['details'] = {
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0...',
            'session_id': 'abc123'
        }
    
    # Add system data for admins only
    if current_user.role == 'admin':
        log_data['system'] = {
            'server': 'server-01',
            'process_id': 12345,
            'memory_usage': '256MB'
        }
    
    return jsonify({
        'log': log_data,
        'viewer': current_user.username,
        'viewer_role': current_user.role
    })


# Example 8: Error Handling with Authentication
@bp_logs_example.route('/risky-operation', methods=['POST'])
@token_required
@role_required('admin')
def risky_operation(current_user):
    """
    Demonstrates error handling in authenticated routes
    """
    try:
        # Your risky operation here
        result = perform_operation()
        
        # Log who performed the operation
        log_audit_trail(
            action='risky_operation',
            user_id=str(current_user._id),
            username=current_user.username,
            role=current_user.role
        )
        
        return jsonify({
            'message': 'Operation successful',
            'performed_by': current_user.username
        })
    
    except Exception as e:
        # Log the error with user context
        log_error(
            error=str(e),
            user_id=str(current_user._id),
            username=current_user.username
        )
        
        return jsonify({
            'error': 'Operation failed',
            'message': str(e)
        }), 500


# Helper functions for demonstration
def perform_operation():
    """Dummy function"""
    return {'status': 'success'}


def log_audit_trail(action, user_id, username, role):
    """Log audit trail"""
    print(f"AUDIT: {action} by {username} ({role}) - ID: {user_id}")


def log_error(error, user_id, username):
    """Log error with context"""
    print(f"ERROR: {error} - User: {username} ({user_id})")


# ============================================================================
# MIGRATION GUIDE FOR YOUR EXISTING ROUTES
# ============================================================================

"""
To protect your existing routes, follow these steps:

1. Import the decorators at the top of your route file:
   
   from app.utils.jwt_utils import token_required, role_required, role_hierarchy_required


2. Add decorators to your route:

   BEFORE:
   @bp.route('/api/logs', methods=['GET'])
   def get_logs():
       logs = fetch_logs()
       return jsonify(logs)
   
   AFTER:
   @bp.route('/api/logs', methods=['GET'])
   @token_required
   @role_hierarchy_required('analyst')
   def get_logs(current_user):
       logs = fetch_logs()
       logger.info(f"Logs accessed by {current_user.username}")
       return jsonify(logs)


3. Choose the right decorator for your needs:

   - @token_required
     Use when: Any authenticated user should have access
     Example: User profile, general queries
   
   - @role_required('admin')
     Use when: Only specific role(s) should have access
     Example: User management, system settings
   
   - @role_hierarchy_required('analyst')
     Use when: Users with this role OR HIGHER should have access
     Example: Analytics, reports, data queries
   
   - @optional_token
     Use when: Route works for both authenticated and anonymous users
     Example: Public data with personalization


4. Decorator Order Matters:

   CORRECT:
   @bp.route('/endpoint')
   @token_required              # First: validate token
   @role_required('admin')      # Second: check role
   def my_route(current_user):
       pass
   
   INCORRECT:
   @bp.route('/endpoint')
   @role_required('admin')      # This won't work without @token_required
   def my_route(current_user):
       pass


5. Update Function Signature:

   All protected routes must accept current_user parameter:
   
   def my_route(current_user):
       # Now you have access to:
       # - current_user.username
       # - current_user.email
       # - current_user.role
       # - current_user.has_role(role_name)
       # etc.


6. Error Handling:

   The decorators automatically handle:
   - Missing tokens (401)
   - Invalid tokens (401)
   - Expired tokens (401)
   - Insufficient permissions (403)
   
   You don't need to add error handling for authentication!
"""

# ============================================================================
# PRACTICAL EXAMPLES FOR YOUR PROJECT
# ============================================================================

"""
Based on your project structure, here's how to protect common routes:


## Logs Routes (backend/app/routes/logs_routes.py)

@bp.route('/upload', methods=['POST'])
@token_required  # Any authenticated user can upload
def upload_logs(current_user):
    # existing code...
    pass


@bp.route('/', methods=['GET'])
@token_required
@role_hierarchy_required('analyst')  # Analyst and above
def get_logs(current_user):
    # existing code...
    pass


## Analytics Routes (backend/app/routes/analytics_routes.py)

@bp.route('/summary', methods=['GET'])
@token_required
@role_hierarchy_required('analyst')  # Analyst and above
def get_analytics_summary(current_user):
    # existing code...
    pass


## Dashboard Routes (backend/app/routes/dashboard_routes.py)

@bp.route('/metrics', methods=['GET'])
@token_required
@role_hierarchy_required('viewer')  # All authenticated users
def get_metrics(current_user):
    # existing code...
    pass


## Fraud Routes (backend/app/routes/fraud_routes.py)

@bp.route('/detect', methods=['POST'])
@token_required
@role_hierarchy_required('analyst')  # Analyst and above
def detect_fraud(current_user):
    # existing code...
    pass


@bp.route('/reports', methods=['GET'])
@token_required
@role_hierarchy_required('moderator')  # Moderator and admin only
def get_fraud_reports(current_user):
    # existing code...
    pass


## Performance Routes (backend/app/routes/performance_routes.py)

@bp.route('/metrics', methods=['GET'])
@token_required
@role_hierarchy_required('analyst')  # Analyst and above
def get_performance_metrics(current_user):
    # existing code...
    pass


## Search Routes (backend/app/routes/search_routes.py)

@bp.route('/', methods=['GET'])
@token_required  # Any authenticated user
def search_logs(current_user):
    # existing code...
    pass
"""
