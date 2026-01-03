"""
User model for authentication and authorization
Stores user profiles in MongoDB
"""

from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import os


class User:
    """User model for MongoDB"""
    
    collection_name = 'users'
    
    # Available roles
    ROLES = {
        'admin': 'Administrator with full access',
        'analyst': 'Data analyst with read and query access',
        'viewer': 'View-only access to dashboards',
        'moderator': 'Can manage users and moderate content'
    }
    
    def __init__(self, username, email, password_hash, role='viewer', 
                 is_active=True, created_at=None, updated_at=None, 
                 last_login=None, _id=None):
        """
        Initialize User object
        
        Args:
            username: Unique username
            email: User email address
            password_hash: Hashed password
            role: User role (admin, analyst, viewer, moderator)
            is_active: Whether the user account is active
            created_at: Creation timestamp
            updated_at: Last update timestamp
            last_login: Last login timestamp
            _id: MongoDB ObjectId
        """
        self._id = _id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role if role in self.ROLES else 'viewer'
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_login = last_login
    
    def to_dict(self, include_password=False):
        """
        Convert user object to dictionary
        
        Args:
            include_password: Whether to include password hash
        
        Returns:
            Dictionary representation of user
        """
        data = {
            '_id': str(self._id) if self._id else None,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_password:
            data['password_hash'] = self.password_hash
        
        return data
    
    def to_mongo(self):
        """
        Convert user object to MongoDB document
        
        Returns:
            Dictionary for MongoDB insertion
        """
        doc = {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login
        }
        
        if self._id:
            doc['_id'] = self._id
        
        return doc
    
    @classmethod
    def from_mongo(cls, doc):
        """
        Create User object from MongoDB document
        
        Args:
            doc: MongoDB document
        
        Returns:
            User object
        """
        if not doc:
            return None
        
        return cls(
            _id=doc.get('_id'),
            username=doc.get('username'),
            email=doc.get('email'),
            password_hash=doc.get('password_hash'),
            role=doc.get('role', 'viewer'),
            is_active=doc.get('is_active', True),
            created_at=doc.get('created_at'),
            updated_at=doc.get('updated_at'),
            last_login=doc.get('last_login')
        )
    
    def has_role(self, required_role):
        """
        Check if user has required role or higher
        
        Role hierarchy: admin > moderator > analyst > viewer
        
        Args:
            required_role: Required role to check
        
        Returns:
            True if user has required role or higher
        """
        role_hierarchy = {
            'viewer': 1,
            'analyst': 2,
            'moderator': 3,
            'admin': 4
        }
        
        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level


class UserRepository:
    """Repository for User database operations"""
    
    def __init__(self, db_client=None):
        """
        Initialize UserRepository
        
        Args:
            db_client: MongoDB client (optional, will create if not provided)
        """
        if db_client:
            self.client = db_client
        else:
            # Create MongoDB client from config
            from config import Config
            mongodb_config = Config.MONGODB_CONFIG
            
            if mongodb_config.get('uri'):
                self.client = MongoClient(mongodb_config['uri'])
            else:
                self.client = MongoClient(
                    host=mongodb_config['host'],
                    port=mongodb_config['port'],
                    username=mongodb_config.get('user'),
                    password=mongodb_config.get('password')
                )
        
        from config import Config
        db_name = Config.MONGODB_CONFIG['database']
        self.db = self.client[db_name]
        self.collection = self.db[User.collection_name]
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes"""
        try:
            # Unique index on username
            self.collection.create_index('username', unique=True)
            # Unique index on email
            self.collection.create_index('email', unique=True)
            # Index on role for queries
            self.collection.create_index('role')
        except Exception as e:
            print(f"Error creating indexes: {e}")
    
    def create(self, user):
        """
        Create a new user
        
        Args:
            user: User object
        
        Returns:
            Created user with ID
        """
        try:
            doc = user.to_mongo()
            result = self.collection.insert_one(doc)
            user._id = result.inserted_id
            return user
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    def find_by_username(self, username):
        """
        Find user by username
        
        Args:
            username: Username to search
        
        Returns:
            User object or None
        """
        doc = self.collection.find_one({'username': username})
        return User.from_mongo(doc)
    
    def find_by_email(self, email):
        """
        Find user by email
        
        Args:
            email: Email to search
        
        Returns:
            User object or None
        """
        doc = self.collection.find_one({'email': email})
        return User.from_mongo(doc)
    
    def find_by_id(self, user_id):
        """
        Find user by ID
        
        Args:
            user_id: User ID (string or ObjectId)
        
        Returns:
            User object or None
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        doc = self.collection.find_one({'_id': user_id})
        return User.from_mongo(doc)
    
    def update(self, user):
        """
        Update user
        
        Args:
            user: User object with updated data
        
        Returns:
            Updated user
        """
        user.updated_at = datetime.utcnow()
        doc = user.to_mongo()
        
        self.collection.update_one(
            {'_id': user._id},
            {'$set': doc}
        )
        
        return user
    
    def update_last_login(self, user_id):
        """
        Update user's last login timestamp
        
        Args:
            user_id: User ID
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        self.collection.update_one(
            {'_id': user_id},
            {'$set': {'last_login': datetime.utcnow()}}
        )
    
    def delete(self, user_id):
        """
        Delete user
        
        Args:
            user_id: User ID (string or ObjectId)
        
        Returns:
            True if deleted
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        result = self.collection.delete_one({'_id': user_id})
        return result.deleted_count > 0
    
    def list_all(self, skip=0, limit=100):
        """
        List all users
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of User objects
        """
        cursor = self.collection.find().skip(skip).limit(limit)
        return [User.from_mongo(doc) for doc in cursor]
    
    def count(self):
        """
        Count total users
        
        Returns:
            Total user count
        """
        return self.collection.count_documents({})
