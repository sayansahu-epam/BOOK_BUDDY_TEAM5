# User Schemas
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    Token,
    TokenData
)

# Book Schemas
from app.schemas.book import (
    ReadingStatus,
    BookGenre,
    BookBase,
    BookCreate,
    BookUpdate,
    BookResponse,
    BookListResponse,
    BookStats
)


# Export all schemas
__all__ = [
    # User
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "Token",
    "TokenData",
    
    # Book
    "ReadingStatus",
    "BookGenre",
    "BookBase",
    "BookCreate",
    "BookUpdate",
    "BookResponse",
    "BookListResponse",
    "BookStats"
]