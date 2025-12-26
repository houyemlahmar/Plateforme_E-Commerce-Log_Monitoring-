"""
Log service module
Handles log processing, ingestion, and management
"""

import logging
import json
import os
import csv
import uuid
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
    
    def process_upload_with_preview(self, file):
        """
        Process uploaded file with preview and queue job
        - Save file to /uploads
        - Extract first 10 lines for preview
        - Insert metadata into MongoDB collection "uploads"
        - Push job ID into Redis queue "ingest_jobs"
        
        Args:
            file: Uploaded file object
        
        Returns:
            dict: Processing result with preview and job ID
        """
        try:
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            # Generate unique job ID
            job_id = str(uuid.uuid4())
            
            # Create uploads directory if not exists
            uploads_dir = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Save file with unique name
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{job_id[:8]}_{filename}"
            file_path = os.path.join(uploads_dir, unique_filename)
            
            # Read file content
            content = file.read().decode('utf-8')
            file_size = len(content.encode('utf-8'))
            
            # Save to disk
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Extract first 10 lines for preview
            lines = content.strip().split('\n')
            preview_lines = lines[:10]
            total_lines = len(lines)
            
            # Parse preview based on file type
            preview = []
            if file_extension == 'json':
                try:
                    # Try parsing as JSON array first
                    json_data = json.loads(content)
                    if isinstance(json_data, list):
                        preview = json_data[:10]
                    else:
                        preview = [json_data]
                except json.JSONDecodeError:
                    # Try parsing as JSONL (JSON lines)
                    for line in preview_lines:
                        if line.strip():
                            try:
                                preview.append(json.loads(line))
                            except json.JSONDecodeError:
                                preview.append({'raw': line, 'error': 'Invalid JSON'})
            elif file_extension == 'csv':
                try:
                    # Parse CSV with DictReader
                    from io import StringIO
                    csv_content = '\n'.join(preview_lines)
                    csv_reader = csv.DictReader(StringIO(csv_content))
                    # Clean CSV data: remove None keys and empty string values
                    preview = []
                    for row in csv_reader:
                        cleaned_row = {
                            str(k): v for k, v in row.items() 
                            if k is not None and v is not None and v.strip() != ''
                        }
                        if cleaned_row:  # Only add non-empty rows
                            preview.append(cleaned_row)
                except Exception as e:
                    logger.warning(f"CSV parsing error: {str(e)}")
                    preview = [{'raw': line} for line in preview_lines]
            else:
                preview = [{'line': i+1, 'content': line} for i, line in enumerate(preview_lines)]
            
            # Store metadata in MongoDB collection "uploads"
            uploaded_at = datetime.utcnow()
            upload_metadata = {
                'job_id': job_id,
                'filename': filename,
                'unique_filename': unique_filename,
                'file_path': file_path,
                'file_size': file_size,
                'file_type': file_extension,
                'total_lines': total_lines,
                'preview': preview[:10],  # Store first 10 lines
                'uploaded_at': uploaded_at,
                'status': 'pending',
                'processed': False
            }
            
            # Insert into MongoDB "uploads" collection
            file_id = self.mongo_service.insert_one('uploads', upload_metadata)
            
            # Push job ID into Redis queue "ingest_jobs"
            job_data = {
                'job_id': job_id,
                'file_id': str(file_id),
                'file_path': file_path,
                'file_type': file_extension,
                'total_lines': total_lines,
                'created_at': uploaded_at.isoformat()
            }
            
            # Push to Redis queue
            self.redis_service.lpush('ingest_jobs', json.dumps(job_data))
            logger.info(f"Job {job_id} pushed to ingest_jobs queue")
            
            return {
                'file_id': str(file_id),
                'job_id': job_id,
                'filename': filename,
                'file_size': file_size,
                'file_type': file_extension,
                'preview': preview,
                'total_lines': total_lines,
                'uploaded_at': uploaded_at.isoformat()
            }
            
        except UnicodeDecodeError as e:
            logger.error(f"File encoding error: {str(e)}")
            raise ValueError("File must be UTF-8 encoded")
        except IOError as e:
            logger.error(f"File I/O error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing upload with preview: {str(e)}", exc_info=True)
            raise
    
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
