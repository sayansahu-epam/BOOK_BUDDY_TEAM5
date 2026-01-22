from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


# ─────────────────────────────────────────────────────────────
# Enum for Reading Status
# ─────────────────────────────────────────────────────────────
class ReadingStatus(str, Enum):
    """
    Allowed values for reading status
    """
    TO_READ = "To Read"
    READING = "Reading"
    COMPLETED = "Completed"


# ─────────────────────────────────────────────────────────────
# Enum for Book Genres
# ─────────────────────────────────────────────────────────────
class BookGenre(str, Enum):
    """
    Allowed values for book genres
    """
    FICTION = "Fiction"
    NON_FICTION = "Non-Fiction"
    MYSTERY = "Mystery"
    SCI_FI = "Sci-Fi"
    BIOGRAPHY = "Biography"
    FANTASY = "Fantasy"
    ROMANCE = "Romance"
    THRILLER = "Thriller"
    SELF_HELP = "Self-Help"
    HISTORY = "History"
    OTHER = "Other"


# ─────────────────────────────────────────────────────────────
# Base Schema (Common Fields)
# ─────────────────────────────────────────────────────────────
class BookBase(BaseModel):
    """
    Base book schema with common fields
    """
    title: str = Field(..., min_length=1, max_length=200, example="The Great Gatsby")
    author: str = Field(..., min_length=1, max_length=100, example="F. Scott Fitzgerald")
    genre: BookGenre = Field(..., example="Fiction")
    start_date: Optional[date] = Field(None, example="2024-01-15")
    end_date: Optional[date] = Field(None, example="2024-02-20")
    status: ReadingStatus = Field(default=ReadingStatus.TO_READ, example="To Read")
    notes: Optional[str] = Field(None, max_length=1000, example="Great book about the American Dream")
    rating: Optional[int] = Field(None, ge=1, le=5, example=5)


# ─────────────────────────────────────────────────────────────
# Schema for Creating New Book
# ─────────────────────────────────────────────────────────────
class BookCreate(BookBase):
    """
    Data required to create a new book entry
    Inherits all fields from BookBase
    """
    pass


# ─────────────────────────────────────────────────────────────
# Schema for Updating Book
# ─────────────────────────────────────────────────────────────
class BookUpdate(BaseModel):
    """
    Data that can be updated (all fields optional)
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    genre: Optional[BookGenre] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[ReadingStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)
    rating: Optional[int] = Field(None, ge=1, le=5)


# ─────────────────────────────────────────────────────────────
# Schema for Book Response (Single Book)
# ─────────────────────────────────────────────────────────────
class BookResponse(BookBase):
    """
    Book data sent back to client
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────
# Schema for Book List Response
# ─────────────────────────────────────────────────────────────
class BookListResponse(BaseModel):
    """
    Response for list of books with count
    """
    total: int
    books: List[BookResponse]


# ─────────────────────────────────────────────────────────────
# Schema for Book Statistics
# ─────────────────────────────────────────────────────────────
class BookStats(BaseModel):
    """
    Reading statistics for dashboard
    """
    total_books: int = 0
    to_read: int = 0
    reading: int = 0
    completed: int = 0
    genres: dict = {}