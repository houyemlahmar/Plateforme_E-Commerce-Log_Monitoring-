"""
Log service module
Handles log processing, ingestion, and management
"""

import logging
import json
from datetime import datetime
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


class LogService:
    """Service for log processing and management"""
    
    def __init__(self, es_service, mongo_service, redis_service):
        """
        Initialize log service
        
        Args:
            es_service: Elasticsearch service instance
            mongo_service: MongoDB service instance
            redis_service: Redis service instance
        """
        self.es_service = es_service
        self.mongo_service = mongo_service
        self.redis_service = redis_service
    
    def process_log_file(self, file):
        """
        Process uploaded log file
        
        Args:
            file: Uploaded file object
        
        Returns:
            dict: Processing result
        """
        try:
            filename = secure_filename(file.filename)
            
            # Read file content
            content = file.read().decode('utf-8')
            lines = content.strip().split('\n')
            
            # Parse and index logs
            documents = []
            for line in lines:
                try:
                    # Try to parse as JSON
                    log_entry = json.loads(line)
                    log_entry['@timestamp'] = datetime.utcnow().isoformat()
                    log_entry['source_file'] = filename
                    documents.append(log_entry)
                except json.JSONDecodeError:
                    # If not JSON, treat as plain text
                    log_entry = {
                        '@timestamp': datetime.utcnow().isoformat(),
                        'message': line,
                        'source_file': filename,
                        'log_type': 'plain'
                    }
                    documents.append(log_entry)
            
            # Bulk index to Elasticsearch
            indexed_count = self.es_service.bulk_index('logs', documents)
            
            # Store metadata in MongoDB
            file_metadata = {
                'filename': filename,
                'uploaded_at': datetime.utcnow(),
                'records_count': len(documents),
                'indexed_count': indexed_count
            }
            file_id = self.mongo_service.insert_one('log_files', file_metadata)
            
            # Invalidate cache
            self.redis_service.delete('logs:recent')
            self.redis_service.delete('logs:stats')
            
            return {
                'records_processed': indexed_count,
                'file_id': str(file_id)
            }
            
        except Exception as e:
            logger.error(f"Error processing log file: {str(e)}")
            raise
    
    def ingest_logs(self, data):
        """
        Ingest logs from JSON payload
        
        Args:
            data: Log data (dict or list)
        
        Returns:
            dict: Ingestion result
        """
        try:
            # Ensure data is a list
            if isinstance(data, dict):
                logs = [data]
            else:
                logs = data
            
            # Add timestamp if not present
            for log in logs:
                if '@timestamp' not in log:
                    log['@timestamp'] = datetime.utcnow().isoformat()
            
            # Bulk index to Elasticsearch
            indexed_count = self.es_service.bulk_index('logs', logs)
            
            # Invalidate cache
            self.redis_service.delete('logs:recent')
            self.redis_service.delete('logs:stats')
            
            return {
                'records_processed': indexed_count
            }
            
        except Exception as e:
            logger.error(f"Error ingesting logs: {str(e)}")
            raise
    
    def get_recent_logs(self, limit=100, log_type=None):
        """
        Get recent logs
        
        Args:
            limit: Number of logs to return
            log_type: Filter by log type
        
        Returns:
            list: Recent logs
        """
        try:
            # Check cache
            cache_key = f"logs:recent:{log_type}:{limit}"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            # Build query
            query = {
                "query": {
                    "bool": {
                        "must": []
                    }
                },
                "sort": [
                    {"@timestamp": {"order": "desc"}}
                ]
            }
            
            if log_type:
                query["query"]["bool"]["must"].append({
                    "term": {"log_type": log_type}
                })
            
            # Search Elasticsearch
            result = self.es_service.search('logs', query, size=limit)
            
            # Extract hits
            logs = [hit['_source'] for hit in result.get('hits', {}).get('hits', [])]
            
            # Cache result
            self.redis_service.set(cache_key, logs, ttl=300)
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting recent logs: {str(e)}")
            raise
    
    def get_logs_statistics(self):
        """
        Get logs statistics
        
        Returns:
            dict: Statistics
        """
        try:
            # Check cache
            cache_key = "logs:stats"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            # Count by log type
            agg_query = {
                "log_types": {
                    "terms": {
                        "field": "log_type.keyword",
                        "size": 10
                    }
                },
                "timeline": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "calendar_interval": "day"
                    }
                }
            }
            
            aggregations = self.es_service.aggregate('logs', agg_query)
            
            # Count total logs in MongoDB
            total_files = self.mongo_service.count_documents('log_files', {})
            
            stats = {
                'total_files': total_files,
                'log_types': [
                    {'type': bucket['key'], 'count': bucket['doc_count']}
                    for bucket in aggregations.get('log_types', {}).get('buckets', [])
                ],
                'timeline': [
                    {'date': bucket['key_as_string'], 'count': bucket['doc_count']}
                    for bucket in aggregations.get('timeline', {}).get('buckets', [])
                ]
            }
            
            # Cache result
            self.redis_service.set(cache_key, stats, ttl=600)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting logs statistics: {str(e)}")
            raise
