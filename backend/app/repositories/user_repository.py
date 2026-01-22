from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User


class UserRepository:
    """
    Repository for User database operations
    Handles all CRUD operations for the users table
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    
    # ─────────────────────────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────────────────────────
    def create(self, username: str, email: str, password_hash: str) -> User:
        """
        Create a new user in database
        
        Args:
            username: User's display name
            email: User's email address
            password_hash: Hashed password (never store plain text!)
            
        Returns:
            Created User object
        """
        db_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    
    # ─────────────────────────────────────────────────────────────
    # READ - Get by ID
    # ─────────────────────────────────────────────────────────────
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    
    # ─────────────────────────────────────────────────────────────
    # READ - Get by Email
    # ─────────────────────────────────────────────────────────────
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address
        
        Args:
            email: User's email address
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()
    
    
    # ─────────────────────────────────────────────────────────────
    # READ - Get by Username
    # ─────────────────────────────────────────────────────────────
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: User's display name
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.username == username).first()
    
    
    # ─────────────────────────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────────────────────────
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Update user information
        
        Args:
            user_id: User's unique identifier
            **kwargs: Fields to update (username, email, password_hash)
            
        Returns:
            Updated User object if found, None otherwise
        """
        db_user = self.get_by_id(user_id)
        
        if db_user is None:
            return None
        
        # Update only provided fields
        for key, value in kwargs.items():
            if value is not None and hasattr(db_user, key):
                setattr(db_user, key, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    
    # ─────────────────────────────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────────────────────────────
    def delete(self, user_id: int) -> bool:
        """
        Delete user from database
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            True if deleted, False if user not found
        """
        db_user = self.get_by_id(user_id)
        
        if db_user is None:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
    
    
    # ─────────────────────────────────────────────────────────────
    # CHECK - Email Exists
    # ─────────────────────────────────────────────────────────────
    def email_exists(self, email: str) -> bool:
        """
        Check if email already exists
        
        Args:
            email: Email to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.db.query(User).filter(User.email == email).first() is not None
    
    
    # ─────────────────────────────────────────────────────────────
    # CHECK - Username Exists
    # ─────────────────────────────────────────────────────────────
    def username_exists(self, username: str) -> bool:
        """
        Check if username already exists
        
        Args:
            username: Username to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.db.query(User).filter(User.username == username).first() is not None