from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.models.book import Book
from app.schemas.book import (
    BookCreate, 
    BookUpdate, 
    BookResponse, 
    BookListResponse,
    BookStats,
    ReadingStatus
)
from app.repositories.book_repository import book_repository


class BookService:
    """
    Business Logic Layer for Book operations
    Handles CRUD operations and statistics
    """
    
    # ─────────────────────────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────────────────────────
    def add_book(
        self, 
        db: Session, 
        book_data: BookCreate, 
        user_id: int
    ) -> Book:
        """
        Add a new book to user's collection
        
        Business Logic:
        1. Validate dates (end_date should be after start_date)
        2. Auto-set status based on dates
        3. Create book in database
        
        Raises:
            ValueError: If validation fails
        """
        
        # Validate dates
        if book_data.start_date and book_data.end_date:
            if book_data.end_date < book_data.start_date:
                raise ValueError("End date cannot be before start date")
        
        # Auto-set status based on dates (if not explicitly set)
        if book_data.end_date and book_data.status != ReadingStatus.COMPLETED:
            # If end_date is set, book should be completed
            book_data.status = ReadingStatus.COMPLETED
        
        # Validate rating
        if book_data.rating is not None:
            if book_data.rating < 1 or book_data.rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        
        # Create book
        book = book_repository.create(db, book_data, user_id)
        
        return book
    
    # ─────────────────────────────────────────────────────────────
    # READ - Single Book
    # ─────────────────────────────────────────────────────────────
    def get_book(
        self, 
        db: Session, 
        book_id: int, 
        user_id: int
    ) -> Optional[Book]:
        """
        Get a single book by ID (only if user owns it)
        
        Returns:
            Book if found and owned by user, None otherwise
        """
        return book_repository.get_by_id_and_user(db, book_id, user_id)
    
    # ─────────────────────────────────────────────────────────────
    # READ - Multiple Books
    # ─────────────────────────────────────────────────────────────
    def get_all_books(
        self, 
        db: Session, 
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> BookListResponse:
        """
        Get all books for a user with pagination
        
        Returns:
            BookListResponse with total count and list of books
        """
        books = book_repository.get_all_by_user(db, user_id, skip, limit)
        total = book_repository.count_by_user(db, user_id)
        
        return BookListResponse(total=total, books=books)
    
    def get_books_by_status(
        self, 
        db: Session, 
        user_id: int, 
        status: str
    ) -> List[Book]:
        """
        Get all books with a specific status
        
        Args:
            status: "To Read", "Reading", or "Completed"
        """
        # Validate status
        valid_statuses = ["To Read", "Reading", "Completed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        return book_repository.get_by_status(db, user_id, status)
    
    def get_books_by_genre(
        self, 
        db: Session, 
        user_id: int, 
        genre: str
    ) -> List[Book]:
        """
        Get all books of a specific genre
        """
        return book_repository.get_by_genre(db, user_id, genre)
    
    def search_books(
        self, 
        db: Session, 
        user_id: int, 
        search_term: str
    ) -> List[Book]:
        """
        Search books by title or author
        """
        if not search_term or len(search_term) < 2:
            raise ValueError("Search term must be at least 2 characters")
        
        return book_repository.search_books(db, user_id, search_term)
    
    # ─────────────────────────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────────────────────────
    def update_book(
        self, 
        db: Session, 
        book_id: int, 
        user_id: int, 
        book_data: BookUpdate
    ) -> Optional[Book]:
        """
        Update an existing book
        
        Business Logic:
        1. Verify user owns the book
        2. Validate dates
        3. Update book
        
        Raises:
            ValueError: If validation fails or book not found
        """
        
        # Check if book exists and user owns it
        existing_book = book_repository.get_by_id_and_user(db, book_id, user_id)
        if not existing_book:
            raise ValueError("Book not found")
        
        # Validate dates if both are provided
        start = book_data.start_date or existing_book.start_date
        end = book_data.end_date or existing_book.end_date
        
        if start and end and end < start:
            raise ValueError("End date cannot be before start date")
        
        # Validate rating
        if book_data.rating is not None:
            if book_data.rating < 1 or book_data.rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        
        # Update book
        updated_book = book_repository.update(db, book_id, user_id, book_data)
        
        return updated_book
    
    def update_status(
        self, 
        db: Session, 
        book_id: int, 
        user_id: int, 
        status: str
    ) -> Optional[Book]:
        """
        Update only the reading status of a book
        
        Also auto-sets dates:
        - "Reading" → sets start_date to today if not set
        - "Completed" → sets end_date to today if not set
        """
        
        # Validate status
        valid_statuses = ["To Read", "Reading", "Completed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        # Get current book
        book = book_repository.get_by_id_and_user(db, book_id, user_id)
        if not book:
            raise ValueError("Book not found")
        
        # Auto-set dates based on status
        update_data = BookUpdate(status=ReadingStatus(status))
        
        if status == "Reading" and not book.start_date:
            update_data.start_date = date.today()
        
        if status == "Completed" and not book.end_date:
            update_data.end_date = date.today()
        
        return book_repository.update(db, book_id, user_id, update_data)
    
    # ─────────────────────────────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────────────────────────────
    def delete_book(
        self, 
        db: Session, 
        book_id: int, 
        user_id: int
    ) -> bool:
        """
        Delete a book
        
        Raises:
            ValueError: If book not found
        """
        
        # Check if book exists
        book = book_repository.get_by_id_and_user(db, book_id, user_id)
        if not book:
            raise ValueError("Book not found")
        
        return book_repository.delete(db, book_id, user_id)
    
    def delete_all_books(self, db: Session, user_id: int) -> int:
        """
        Delete all books for a user
        
        Returns:
            Number of books deleted
        """
        return book_repository.delete_all_by_user(db, user_id)
    
    # ─────────────────────────────────────────────────────────────
    # STATISTICS
    # ─────────────────────────────────────────────────────────────
    def get_statistics(self, db: Session, user_id: int) -> BookStats:
        """
        Get reading statistics for a user
        
        Returns:
            BookStats with counts and genre breakdown
        """
        stats = book_repository.get_stats(db, user_id)
        
        return BookStats(
            total_books=stats["total_books"],
            to_read=stats["to_read"],
            reading=stats["reading"],
            completed=stats["completed"],
            genres=stats["genres"]
        )
    
    # ─────────────────────────────────────────────────────────────
    # UTILITY METHODS
    # ─────────────────────────────────────────────────────────────
    def mark_as_reading(self, db: Session, book_id: int, user_id: int) -> Optional[Book]:
        """
        Quick method to mark a book as "Reading"
        """
        return self.update_status(db, book_id, user_id, "Reading")
    
    def mark_as_completed(self, db: Session, book_id: int, user_id: int) -> Optional[Book]:
        """
        Quick method to mark a book as "Completed"
        """
        return self.update_status(db, book_id, user_id, "Completed")
    
    def get_currently_reading(self, db: Session, user_id: int) -> List[Book]:
        """
        Get all books currently being read
        """
        return self.get_books_by_status(db, user_id, "Reading")
    
    def get_completed_books(self, db: Session, user_id: int) -> List[Book]:
        """
        Get all completed books
        """
        return self.get_books_by_status(db, user_id, "Completed")
    
    def get_to_read_books(self, db: Session, user_id: int) -> List[Book]:
        """
        Get all books in "To Read" list
        """
        return self.get_books_by_status(db, user_id, "To Read")


# Create a singleton instance
book_service = BookService()