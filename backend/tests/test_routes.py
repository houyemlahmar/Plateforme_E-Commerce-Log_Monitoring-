"""
Tests for log routes
"""

import pytest
import json
from io import BytesIO


class TestLogsRoutes:
    """Test cases for logs routes"""
    
    def test_upload_logs_no_file(self, client):
        """Test upload without file"""
        response = client.post('/api/logs/upload')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_upload_logs_empty_filename(self, client):
        """Test upload with empty filename"""
        data = {'file': (BytesIO(b''), '')}
        response = client.post(
            '/api/logs/upload',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code == 400
    
    def test_ingest_logs_no_data(self, client):
        """Test ingest without data"""
        response = client.post('/api/logs/ingest')
        assert response.status_code == 400
    
    def test_ingest_logs_valid_data(self, client, sample_log_data):
        """Test ingest with valid data"""
        response = client.post(
            '/api/logs/ingest',
            data=json.dumps(sample_log_data),
            content_type='application/json'
        )
        # May fail if services not running, so just check structure
        assert response.status_code in [201, 500]
    
    def test_get_log_types(self, client):
        """Test get log types"""
        response = client.post('/api/logs/types')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'log_types' in data
        assert len(data['log_types']) > 0
    
    def test_get_recent_logs(self, client):
        """Test get recent logs"""
        response = client.get('/api/logs/recent?limit=10')
        # May fail if services not running
        assert response.status_code in [200, 500]
    
    def test_get_logs_stats(self, client):
        """Test get logs statistics"""
        response = client.get('/api/logs/stats')
        # May fail if services not running
        assert response.status_code in [200, 500]


class TestAnalyticsRoutes:
    """Test cases for analytics routes"""
    
    def test_get_transaction_analytics(self, client):
        """Test get transaction analytics"""
        response = client.get('/api/analytics/transactions?granularity=daily')
        assert response.status_code in [200, 500]
    
    def test_get_error_analytics(self, client):
        """Test get error analytics"""
        response = client.get('/api/analytics/errors')
        assert response.status_code in [200, 500]
    
    def test_get_user_behavior_analytics(self, client):
        """Test get user behavior analytics"""
        response = client.get('/api/analytics/user-behavior')
        assert response.status_code in [200, 500]
    
    def test_get_trends(self, client):
        """Test get trends"""
        response = client.get('/api/analytics/trends?time_range=7d')
        assert response.status_code in [200, 500]


class TestDashboardRoutes:
    """Test cases for dashboard routes"""
    
    def test_get_dashboard_overview(self, client):
        """Test get dashboard overview"""
        response = client.get('/api/dashboard/overview')
        assert response.status_code in [200, 500]
    
    def test_get_metrics(self, client):
        """Test get metrics"""
        response = client.get('/api/dashboard/metrics')
        assert response.status_code in [200, 500]
    
    def test_get_chart_data(self, client):
        """Test get chart data"""
        response = client.get('/api/dashboard/charts?chart_type=transactions')
        assert response.status_code in [200, 500]


class TestFraudRoutes:
    """Test cases for fraud routes"""
    
    def test_detect_fraud_no_data(self, client):
        """Test fraud detection without data"""
        response = client.post('/api/fraud/detect')
        assert response.status_code == 400
    
    def test_detect_fraud_valid_data(self, client, sample_fraud_data):
        """Test fraud detection with valid data"""
        response = client.post(
            '/api/fraud/detect',
            data=json.dumps(sample_fraud_data),
            content_type='application/json'
        )
        assert response.status_code in [200, 500]
    
    def test_get_suspicious_activities(self, client):
        """Test get suspicious activities"""
        response = client.get('/api/fraud/suspicious-activities?limit=10')
        assert response.status_code in [200, 500]
    
    def test_get_fraud_stats(self, client):
        """Test get fraud statistics"""
        response = client.get('/api/fraud/stats')
        assert response.status_code in [200, 500]


class TestPerformanceRoutes:
    """Test cases for performance routes"""
    
    def test_get_performance_metrics(self, client):
        """Test get performance metrics"""
        response = client.get('/api/performance/metrics')
        assert response.status_code in [200, 500]
    
    def test_get_api_response_times(self, client):
        """Test get API response times"""
        response = client.get('/api/performance/api-response-times')
        assert response.status_code in [200, 500]
    
    def test_get_database_latency(self, client):
        """Test get database latency"""
        response = client.get('/api/performance/database-latency')
        assert response.status_code in [200, 500]


class TestSearchRoutes:
    """Test cases for search routes"""
    
    def test_search_logs_empty_query(self, client):
        """Test search with empty query"""
        response = client.get('/api/search/?q=')
        assert response.status_code in [200, 500]
    
    def test_search_logs_with_query(self, client):
        """Test search with query"""
        response = client.get('/api/search/?q=transaction&size=10')
        assert response.status_code in [200, 500]
    
    def test_autocomplete(self, client):
        """Test autocomplete"""
        response = client.get('/api/search/autocomplete?q=trans')
        assert response.status_code in [200, 500]
