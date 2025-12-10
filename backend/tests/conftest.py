"""
Test configuration and fixtures
"""

import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def sample_log_data():
    """Sample log data for testing"""
    return {
        'message': 'Test log entry',
        'log_type': 'transaction',
        'level': 'INFO',
        'transaction_id': 'TXN12345',
        'user_id': 'USER123',
        'amount': 99.99,
        'currency': 'USD',
        'payment_method': 'credit_card',
        'status': 'completed'
    }


@pytest.fixture
def sample_transaction():
    """Sample transaction data for testing"""
    return {
        'transaction_id': 'TXN12345',
        'user_id': 'USER123',
        'amount': 150.00,
        'currency': 'USD',
        'payment_method': 'credit_card',
        'status': 'completed',
        'timestamp': '2024-01-01T12:00:00Z'
    }


@pytest.fixture
def sample_fraud_data():
    """Sample fraud detection data for testing"""
    return {
        'transaction_id': 'TXN99999',
        'user_id': 'USER999',
        'amount': 15000.00,
        'currency': 'USD',
        'payment_method': 'credit_card',
        'location': 'XX',
        'client_ip': '192.168.1.100'
    }
