from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.repositories.user_repository import user_repository
from app.utils.security import hash_password, verify_password


class UserService:
    """
    Business Logic Layer for User operations
    Handles profile management
    """
    
    # ─────────────────────────────────────────────────────────────
    # GET PROFILE
    # ─────────────────────────────────────────────────────────────
    def get_profile(self, db: Session, user_id: int) -> Optional[User]:
        """
        Get user profile by ID
        
        Returns:
            User object if found, None otherwise
        """
        return user_repository.get_by_id(db, user_id)
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get user by email
        
        Returns:
            User object if found, None otherwise
        """
        return user_repository.get_by_email(db, email)
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Get user by username
        
        Returns:
            User object if found, None otherwise
        """
        return user_repository.get_by_username(db, username)
    
    # ─────────────────────────────────────────────────────────────
    # UPDATE PROFILE
    # ─────────────────────────────────────────────────────────────
    def update_profile(
        self, 
        db: Session, 
        user_id: int, 
        user_data: UserUpdate
    ) -> Optional[User]:
        """
        Update user profile
        
        Business Logic:
        1. Check if new email is already taken (if changing email)
        2. Check if new username is already taken (if changing username)
        3. Update user in database
        
        Raises:
            ValueError: If email or username already taken
        """
        
        # Get current user
        current_user = user_repository.get_by_id(db, user_id)
        if not current_user:
            raise ValueError("User not found")
        
        # Check if new email is already taken
        if user_data.email and user_data.email != current_user.email:
            existing_email = user_repository.get_by_email(db, user_data.email)
            if existing_email:
                raise ValueError("Email already registered")
        
        # Check if new username is already taken
        if user_data.username and user_data.username != current_user.username:
            existing_username = user_repository.get_by_username(db, user_data.username)
            if existing_username:
                raise ValueError("Username already taken")
        
        # Update user
        updated_user = user_repository.update(db, user_id, user_data)
        
        return updated_user
    
    # ─────────────────────────────────────────────────────────────
    # CHANGE PASSWORD
    # ─────────────────────────────────────────────────────────────
    def change_password(
        self, 
        db: Session, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Change user password
        
        Business Logic:
        1. Verify current password
        2. Hash new password
        3. Update password in database
        
        Raises:
            ValueError: If current password is incorrect
        """
        
        # Get user
        user = user_repository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Hash new password
        new_password_hash = hash_password(new_password)
        
        # Update password
        user_repository.update_password(db, user_id, new_password_hash)
        
        return True
    
    # ─────────────────────────────────────────────────────────────
    # DELETE ACCOUNT
    # ─────────────────────────────────────────────────────────────
    def delete_account(
        self, 
        db: Session, 
        user_id: int, 
        password: str
    ) -> bool:
        """
        Delete user account
        
        Business Logic:
        1. Verify password (for security)
        2. Delete all user's books
        3. Delete user account
        
        Raises:
            ValueError: If password is incorrect
        """
        
        # Get user
        user = user_repository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify password for security
        if not verify_password(password, user.password_hash):
            raise ValueError("Password is incorrect")
        
        # Delete user (books will be deleted automatically due to cascade)
        user_repository.delete(db, user_id)
        
        return True
    
    # ─────────────────────────────────────────────────────────────
    # CHECK IF EXISTS
    # ─────────────────────────────────────────────────────────────
    def email_exists(self, db: Session, email: str) -> bool:
        """
        Check if email is already registered
        """
        return user_repository.get_by_email(db, email) is not None
    
    def username_exists(self, db: Session, username: str) -> bool:
        """
        Check if username is already taken
        """
        return user_repository.get_by_username(db, username) is not None


# Create a singleton instance
user_service = UserService()