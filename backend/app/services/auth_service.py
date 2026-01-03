"""
Authentication service
Handles user authentication, password hashing, and user management
"""

import bcrypt
import logging
from datetime import datetime
from app.models.user_model import User, UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        """Initialize AuthService"""
        self.user_repo = UserRepository()
    
    @staticmethod
    def hash_password(password):
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """
        Verify a password against its hash
        
        Args:
            password: Plain text password
            password_hash: Hashed password
        
        Returns:
            True if password matches
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    def register_user(self, username, email, password, role='viewer'):
        """
        Register a new user
        
        Args:
            username: Unique username
            email: User email
            password: Plain text password
            role: User role (default: viewer)
        
        Returns:
            Created user object
        
        Raises:
            ValueError: If username or email already exists
        """
        # Validate inputs
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not email or '@' not in email:
            raise ValueError("Invalid email address")
        
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if role not in User.ROLES:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(User.ROLES.keys())}")
        
        # Check if username already exists
        existing_user = self.user_repo.find_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")
        
        # Check if email already exists
        existing_email = self.user_repo.find_by_email(email)
        if existing_email:
            raise ValueError("Email already exists")
        
        # Create user
        password_hash = self.hash_password(password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True
        )
        
        created_user = self.user_repo.create(user)
        logger.info(f"User registered: {username} (role: {role})")
        
        return created_user
    
    def authenticate_user(self, username, password):
        """
        Authenticate a user with username and password
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            User object if authentication successful
        
        Raises:
            ValueError: If authentication fails
        """
        # Find user
        user = self.user_repo.find_by_username(username)
        
        if not user:
            logger.warning(f"Authentication failed: User not found - {username}")
            raise ValueError("Invalid username or password")
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Authentication failed: Inactive user - {username}")
            raise ValueError("User account is inactive")
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: Invalid password - {username}")
            raise ValueError("Invalid username or password")
        
        # Update last login
        self.user_repo.update_last_login(user._id)
        
        logger.info(f"User authenticated: {username}")
        return user
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID
        
        Args:
            user_id: User ID
        
        Returns:
            User object or None
        """
        return self.user_repo.find_by_id(user_id)
    
    def get_user_by_username(self, username):
        """
        Get user by username
        
        Args:
            username: Username
        
        Returns:
            User object or None
        """
        return self.user_repo.find_by_username(username)
    
    def update_user_password(self, user_id, old_password, new_password):
        """
        Update user password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
        
        Returns:
            True if password updated
        
        Raises:
            ValueError: If old password is incorrect or new password is invalid
        """
        user = self.user_repo.find_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        # Verify old password
        if not self.verify_password(old_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Validate new password
        if not new_password or len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters long")
        
        # Update password
        user.password_hash = self.hash_password(new_password)
        self.user_repo.update(user)
        
        logger.info(f"Password updated for user: {user.username}")
        return True
    
    def update_user_role(self, user_id, new_role):
        """
        Update user role (admin only)
        
        Args:
            user_id: User ID
            new_role: New role
        
        Returns:
            Updated user
        
        Raises:
            ValueError: If role is invalid
        """
        if new_role not in User.ROLES:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(User.ROLES.keys())}")
        
        user = self.user_repo.find_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        user.role = new_role
        updated_user = self.user_repo.update(user)
        
        logger.info(f"Role updated for user {user.username}: {new_role}")
        return updated_user
    
    def deactivate_user(self, user_id):
        """
        Deactivate a user account
        
        Args:
            user_id: User ID
        
        Returns:
            Updated user
        """
        user = self.user_repo.find_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        user.is_active = False
        updated_user = self.user_repo.update(user)
        
        logger.info(f"User deactivated: {user.username}")
        return updated_user
    
    def activate_user(self, user_id):
        """
        Activate a user account
        
        Args:
            user_id: User ID
        
        Returns:
            Updated user
        """
        user = self.user_repo.find_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        user.is_active = True
        updated_user = self.user_repo.update(user)
        
        logger.info(f"User activated: {user.username}")
        return updated_user
    
    def list_users(self, skip=0, limit=100):
        """
        List all users
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
        
        Returns:
            List of users (without password hashes)
        """
        users = self.user_repo.list_all(skip=skip, limit=limit)
        return [user.to_dict() for user in users]
    
    def delete_user(self, user_id):
        """
        Delete a user
        
        Args:
            user_id: User ID
        
        Returns:
            True if deleted
        """
        deleted = self.user_repo.delete(user_id)
        
        if deleted:
            logger.info(f"User deleted: {user_id}")
        
        return deleted
