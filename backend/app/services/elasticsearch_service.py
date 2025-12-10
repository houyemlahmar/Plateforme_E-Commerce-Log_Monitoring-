"""
Elasticsearch service module
Handles Elasticsearch operations for log indexing and search
"""

import logging
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as es_exceptions

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Service for Elasticsearch operations"""
    
    def __init__(self, config):
        """
        Initialize Elasticsearch service
        
        Args:
            config: Elasticsearch configuration dictionary
        """
        self.config = config
        self.index_prefix = config.get('index_prefix', 'ecommerce-logs')
        
        try:
            self.client = Elasticsearch(
                [f"http://{config['host']}:{config['port']}"],
                basic_auth=(config.get('user'), config.get('password')) if config.get('user') else None
            )
            
            # Test connection
            if self.client.ping():
                logger.info("Successfully connected to Elasticsearch")
            else:
                logger.error("Failed to connect to Elasticsearch")
                
        except Exception as e:
            logger.error(f"Error initializing Elasticsearch: {str(e)}")
            raise
    
    def create_index(self, index_name, mappings=None):
        """
        Create an index with optional mappings
        
        Args:
            index_name: Name of the index
            mappings: Index mappings
        
        Returns:
            bool: Success status
        """
        try:
            full_index_name = f"{self.index_prefix}-{index_name}"
            
            if self.client.indices.exists(index=full_index_name):
                logger.info(f"Index {full_index_name} already exists")
                return True
            
            body = {"mappings": mappings} if mappings else {}
            self.client.indices.create(index=full_index_name, body=body)
            logger.info(f"Created index: {full_index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            return False
    
    def index_document(self, index_name, document, doc_id=None):
        """
        Index a document
        
        Args:
            index_name: Name of the index
            document: Document to index
            doc_id: Optional document ID
        
        Returns:
            dict: Indexing result
        """
        try:
            full_index_name = f"{self.index_prefix}-{index_name}"
            
            result = self.client.index(
                index=full_index_name,
                id=doc_id,
                document=document
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error indexing document: {str(e)}")
            raise
    
    def bulk_index(self, index_name, documents):
        """
        Bulk index documents
        
        Args:
            index_name: Name of the index
            documents: List of documents to index
        
        Returns:
            int: Number of documents indexed
        """
        try:
            from elasticsearch.helpers import bulk
            
            full_index_name = f"{self.index_prefix}-{index_name}"
            
            actions = [
                {
                    "_index": full_index_name,
                    "_source": doc
                }
                for doc in documents
            ]
            
            success, _ = bulk(self.client, actions)
            logger.info(f"Bulk indexed {success} documents")
            return success
            
        except Exception as e:
            logger.error(f"Error bulk indexing: {str(e)}")
            raise
    
    def search(self, index_name, query, size=100):
        """
        Search documents
        
        Args:
            index_name: Name of the index
            query: Elasticsearch query
            size: Number of results
        
        Returns:
            dict: Search results
        """
        try:
            full_index_name = f"{self.index_prefix}-{index_name}"
            
            result = self.client.search(
                index=full_index_name,
                body=query,
                size=size
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            raise
    
    def aggregate(self, index_name, aggregations):
        """
        Execute aggregation query
        
        Args:
            index_name: Name of the index
            aggregations: Aggregation query
        
        Returns:
            dict: Aggregation results
        """
        try:
            full_index_name = f"{self.index_prefix}-{index_name}"
            
            result = self.client.search(
                index=full_index_name,
                body={"aggs": aggregations},
                size=0
            )
            
            return result.get('aggregations', {})
            
        except Exception as e:
            logger.error(f"Error executing aggregation: {str(e)}")
            raise
    
    def delete_index(self, index_name):
        """
        Delete an index
        
        Args:
            index_name: Name of the index
        
        Returns:
            bool: Success status
        """
        try:
            full_index_name = f"{self.index_prefix}-{index_name}"
            
            if self.client.indices.exists(index=full_index_name):
                self.client.indices.delete(index=full_index_name)
                logger.info(f"Deleted index: {full_index_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting index: {str(e)}")
            return False
