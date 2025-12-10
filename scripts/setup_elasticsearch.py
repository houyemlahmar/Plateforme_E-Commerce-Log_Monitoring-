#!/usr/bin/env python3
"""
Script to initialize Elasticsearch indices and Kibana dashboards
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.services.elasticsearch_service import ElasticsearchService


def create_indices(es_service):
    """Create Elasticsearch indices with mappings"""
    
    # Logs index mapping
    logs_mapping = {
        "properties": {
            "@timestamp": {"type": "date"},
            "log_type": {"type": "keyword"},
            "level": {"type": "keyword"},
            "message": {"type": "text"},
            "user_id": {"type": "keyword"},
            "transaction_id": {"type": "keyword"},
            "amount": {"type": "float"},
            "currency": {"type": "keyword"},
            "payment_method": {"type": "keyword"},
            "status": {"type": "keyword"},
            "error_code": {"type": "integer"},
            "error_type": {"type": "keyword"},
            "error_message": {"type": "text"},
            "endpoint": {"type": "keyword"},
            "method": {"type": "keyword"},
            "response_time": {"type": "float"},
            "db_query_time": {"type": "float"},
            "fraud_score": {"type": "integer"},
            "fraud_detected": {"type": "boolean"},
            "fraud_indicators": {"type": "keyword"},
            "action": {"type": "keyword"},
            "page": {"type": "keyword"},
            "session_id": {"type": "keyword"},
            "geoip": {
                "properties": {
                    "location": {"type": "geo_point"},
                    "country_name": {"type": "keyword"},
                    "city_name": {"type": "keyword"}
                }
            }
        }
    }
    
    print("Creating logs index...")
    if es_service.create_index('logs', logs_mapping):
        print("✓ Logs index created successfully")
    else:
        print("✗ Failed to create logs index")


def main():
    """Main function"""
    # Configuration
    config = {
        'host': 'localhost',
        'port': 9200,
        'index_prefix': 'ecommerce-logs'
    }
    
    print("Initializing Elasticsearch setup...")
    print(f"Connecting to Elasticsearch at {config['host']}:{config['port']}...")
    
    try:
        # Create Elasticsearch service
        es_service = ElasticsearchService(config)
        
        # Wait for Elasticsearch to be ready
        print("Waiting for Elasticsearch to be ready...")
        max_retries = 30
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if es_service.client.ping():
                    print("✓ Elasticsearch is ready")
                    break
            except Exception:
                pass
            
            retry_count += 1
            time.sleep(2)
            print(f"Retry {retry_count}/{max_retries}...")
        
        if retry_count >= max_retries:
            print("✗ Elasticsearch is not responding")
            return 1
        
        # Create indices
        create_indices(es_service)
        
        print("\n✓ Elasticsearch setup completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n✗ Error during setup: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
