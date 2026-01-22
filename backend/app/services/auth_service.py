from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.repositories.user_repository import user_repository
from app.utils.security import hash_password, verify_password, create_access_token
from app.config import settings


class AuthService:
    """
    Business Logic Layer for Authentication
    Handles registration, login, and token generation
    """
    
    # ─────────────────────────────────────────────────────────────
    # REGISTER
    # ─────────────────────────────────────────────────────────────
    def register(self, db: Session, user_data: UserCreate) -> dict:
        """
        Register a new user
        
        Business Logic:
        1. Check if email already exists
        2. Check if username already exists
        3. Hash the password
        4. Create user in database
        5. Generate access token
        6. Return user + token
        
        Raises:
            ValueError: If email or username already exists
        """
        
        # Check if email already exists
        existing_email = user_repository.get_by_email(db, user_data.email)
        if existing_email:
            raise ValueError("Email already registered")
        
        # Check if username already exists
        existing_username = user_repository.get_by_username(db, user_data.username)
        if existing_username:
            raise ValueError("Username already taken")
        
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Create user in database
        user = user_repository.create(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        return {
            "user": user,
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    # ─────────────────────────────────────────────────────────────
    # LOGIN
    # ─────────────────────────────────────────────────────────────
    def login(self, db: Session, login_data: UserLogin) -> dict:
        """
        Authenticate user and return token
        
        Business Logic:
        1. Find user by email
        2. Verify password
        3. Generate access token
        4. Return token
        
        Raises:
            ValueError: If credentials are invalid
        """
        
        # Find user by email
        user = user_repository.get_by_email(db, login_data.email)
        
        if not user:
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    # ─────────────────────────────────────────────────────────────
    # AUTHENTICATE (Verify credentials without generating token)
    # ─────────────────────────────────────────────────────────────
    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
        """
        Verify user credentials
        
        Returns:
            User object if credentials valid, None otherwise
        """
        
        user = user_repository.get_by_email(db, email)
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    # ─────────────────────────────────────────────────────────────
    # GENERATE TOKEN (For existing user)
    # ─────────────────────────────────────────────────────────────
    def create_token_for_user(self, user: User, expires_minutes: int = None) -> Token:
        """
        Generate a new token for an existing user
        
        Args:
            user: User object
            expires_minutes: Optional custom expiration time
        
        Returns:
            Token object with access_token and token_type
        """
        
        expires_delta = None
        if expires_minutes:
            expires_delta = timedelta(minutes=expires_minutes)
        
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=expires_delta
        )
        
        return Token(access_token=access_token, token_type="bearer")


# Create a singleton instance
auth_service = AuthService()