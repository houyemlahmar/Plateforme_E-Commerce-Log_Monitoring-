"""
MongoDB service module
Handles MongoDB operations for metadata storage
"""

import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


class MongoDBService:
    """Service for MongoDB operations"""
    
    def __init__(self, config):
        """
        Initialize MongoDB service
        
        Args:
            config: MongoDB configuration dictionary
        """
        self.config = config
        
        try:
            # Use URI if provided, otherwise construct from components
            if config.get('uri'):
                self.client = MongoClient(config['uri'])
            else:
                self.client = MongoClient(
                    host=config.get('host', 'localhost'),
                    port=config.get('port', 27017),
                    username=config.get('user'),
                    password=config.get('password'),
                    authSource='admin'
                )
            
            self.db = self.client[config.get('database', 'ecommerce_logs')]
            
            # Test connection
            self.client.server_info()
            logger.info("Successfully connected to MongoDB")
            
        except PyMongoError as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise
    
    def insert_one(self, collection_name, document):
        """
        Insert a single document
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
        
        Returns:
            ObjectId: Inserted document ID
        """
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            return result.inserted_id
            
        except PyMongoError as e:
            logger.error(f"Error inserting document: {str(e)}")
            raise
    
    def insert_many(self, collection_name, documents):
        """
        Insert multiple documents
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to insert
        
        Returns:
            list: List of inserted document IDs
        """
        try:
            collection = self.db[collection_name]
            result = collection.insert_many(documents)
            return result.inserted_ids
            
        except PyMongoError as e:
            logger.error(f"Error inserting documents: {str(e)}")
            raise
    
    def find_one(self, collection_name, query):
        """
        Find a single document
        
        Args:
            collection_name: Name of the collection
            query: Query filter
        
        Returns:
            dict: Found document or None
        """
        try:
            collection = self.db[collection_name]
            return collection.find_one(query)
            
        except PyMongoError as e:
            logger.error(f"Error finding document: {str(e)}")
            raise
    
    def find(self, collection_name, query, limit=100, sort=None):
        """
        Find multiple documents
        
        Args:
            collection_name: Name of the collection
            query: Query filter
            limit: Maximum number of documents
            sort: Sort specification
        
        Returns:
            list: List of documents
        """
        try:
            collection = self.db[collection_name]
            cursor = collection.find(query).limit(limit)
            
            if sort:
                cursor = cursor.sort(sort)
            
            return list(cursor)
            
        except PyMongoError as e:
            logger.error(f"Error finding documents: {str(e)}")
            raise
    
    def update_one(self, collection_name, query, update):
        """
        Update a single document
        
        Args:
            collection_name: Name of the collection
            query: Query filter
            update: Update operations
        
        Returns:
            int: Number of modified documents
        """
        try:
            collection = self.db[collection_name]
            result = collection.update_one(query, update)
            return result.modified_count
            
        except PyMongoError as e:
            logger.error(f"Error updating document: {str(e)}")
            raise
    
    def delete_one(self, collection_name, query):
        """
        Delete a single document
        
        Args:
            collection_name: Name of the collection
            query: Query filter
        
        Returns:
            int: Number of deleted documents
        """
        try:
            collection = self.db[collection_name]
            result = collection.delete_one(query)
            return result.deleted_count
            
        except PyMongoError as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def aggregate(self, collection_name, pipeline):
        """
        Execute aggregation pipeline
        
        Args:
            collection_name: Name of the collection
            pipeline: Aggregation pipeline
        
        Returns:
            list: Aggregation results
        """
        try:
            collection = self.db[collection_name]
            return list(collection.aggregate(pipeline))
            
        except PyMongoError as e:
            logger.error(f"Error executing aggregation: {str(e)}")
            raise
    
    def count_documents(self, collection_name, query):
        """
        Count documents matching query
        
        Args:
            collection_name: Name of the collection
            query: Query filter
        
        Returns:
            int: Number of documents
        """
        try:
            collection = self.db[collection_name]
            return collection.count_documents(query)
            
        except PyMongoError as e:
            logger.error(f"Error counting documents: {str(e)}")
            raise
