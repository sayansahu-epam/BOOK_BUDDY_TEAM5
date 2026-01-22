from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Generator
from app.database import SessionLocal
from app.utils.security import decode_token
from app.models.user import User


# ─────────────────────────────────────────────────────────────
# OAuth2 Scheme - Extracts token from Authorization header
# ─────────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ─────────────────────────────────────────────────────────────
# Database Session Dependency
# ─────────────────────────────────────────────────────────────
def get_db() -> Generator:
    """
    Creates a new database session for each request.
    Automatically closes session when request is complete.
    
    Usage in router:
        @router.get("/books")
        def get_books(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────
# Get Current User Dependency
# ─────────────────────────────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts and validates JWT token, returns current user.
    
    Raises:
        HTTPException 401 if token is invalid or user not found
    
    Usage in router:
        @router.get("/books")
        def get_books(current_user: User = Depends(get_current_user)):
            # current_user is now available!
            ...
    """
    
    # Exception to raise if authentication fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the token
    token_data = decode_token(token)
    
    if token_data is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    
    if user is None:
        raise credentials_exception
    
    return user


# ─────────────────────────────────────────────────────────────
# Optional: Get Current User (doesn't raise error if not logged in)
# ─────────────────────────────────────────────────────────────
def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User | None:
    """
    Same as get_current_user but returns None instead of raising error.
    Useful for endpoints that work for both logged-in and anonymous users.
    """
    try:
        return get_current_user(token, db)
    except HTTPException:
        return None