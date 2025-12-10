"""
Routes package initialization
"""

from . import logs_routes
from . import analytics_routes
from . import dashboard_routes
from . import fraud_routes
from . import performance_routes
from . import search_routes

__all__ = [
    'logs_routes',
    'analytics_routes',
    'dashboard_routes',
    'fraud_routes',
    'performance_routes',
    'search_routes'
]
