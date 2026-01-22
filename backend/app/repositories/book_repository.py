from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate, ReadingStatus


class BookRepository:
    """
    Data Access Layer for Book operations
    Handles all database CRUD operations for books
    """
    
    # ─────────────────────────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────────────────────────
    def create(self, db: Session, book_data: BookCreate, user_id: int) -> Book:
        """
        Create a new book entry in database
        """
        db_book = Book(
            user_id=user_id,
            title=book_data.title,
            author=book_data.author,
            genre=book_data.genre.value if book_data.genre else None,
            start_date=book_data.start_date,
            end_date=book_data.end_date,
            status=book_data.status.value if book_data.status else "To Read",
            notes=book_data.notes,
            rating=book_data.rating
        )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    
    # ─────────────────────────────────────────────────────────────
    # READ - Single Book
    # ─────────────────────────────────────────────────────────────
    def get_by_id(self, db: Session, book_id: int) -> Optional[Book]:
        """
        Get a book by its ID
        """
        return db.query(Book).filter(Book.id == book_id).first()
    
    def get_by_id_and_user(self, db: Session, book_id: int, user_id: int) -> Optional[Book]:
        """
        Get a book by ID and User ID (ensures user owns the book)
        """
        return db.query(Book).filter(
            Book.id == book_id,
            Book.user_id == user_id
        ).first()
    
    # ─────────────────────────────────────────────────────────────
    # READ - Multiple Books
    # ─────────────────────────────────────────────────────────────
    def get_all_by_user(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Book]:
        """
        Get all books for a specific user with pagination
        """
        return db.query(Book).filter(
            Book.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_by_status(
        self, 
        db: Session, 
        user_id: int, 
        status: str
    ) -> List[Book]:
        """
        Get all books with a specific status for a user
        """
        return db.query(Book).filter(
            Book.user_id == user_id,
            Book.status == status
        ).all()
    
    def get_by_genre(
        self, 
        db: Session, 
        user_id: int, 
        genre: str
    ) -> List[Book]:
        """
        Get all books of a specific genre for a user
        """
        return db.query(Book).filter(
            Book.user_id == user_id,
            Book.genre == genre
        ).all()
    
    def search_books(
        self, 
        db: Session, 
        user_id: int, 
        search_term: str
    ) -> List[Book]:
        """
        Search books by title or author
        """
        search = f"%{search_term}%"
        return db.query(Book).filter(
            Book.user_id == user_id,
            (Book.title.ilike(search) | Book.author.ilike(search))
        ).all()
    
    # ─────────────────────────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────────────────────────
    def update(
        self, 
        db: Session, 
        book_id: int, 
        user_id: int, 
        book_data: BookUpdate
    ) -> Optional[Book]:
        """
        Update an existing book
        """
        db_book = self.get_by_id_and_user(db, book_id, user_id)
        
        if not db_book:
            return None
        
        # Update only provided fields
        update_data = book_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            # Handle enum values
            if field == "status" and value is not None:
                value = value.value if hasattr(value, 'value') else value
            if field == "genre" and value is not None:
                value = value.value if hasattr(value, 'value') else value
            
            setattr(db_book, field, value)
        
        db.commit()
        db.refresh(db_book)
        return db_book
    
    def update_status(
        self, 
        db: Session, 
        book_id: int, 
        user_id: int, 
        status: str
    ) -> Optional[Book]:
        """
        Update only the reading status of a book
        """
        db_book = self.get_by_id_and_user(db, book_id, user_id)
        
        if not db_book:
            return None
        
        db_book.status = status
        db.commit()
        db.refresh(db_book)
        return db_book
    
    # ─────────────────────────────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────────────────────────────
    def delete(self, db: Session, book_id: int, user_id: int) -> bool:
        """
        Delete a book by ID (only if user owns it)
        """
        db_book = self.get_by_id_and_user(db, book_id, user_id)
        
        if not db_book:
            return False
        
        db.delete(db_book)
        db.commit()
        return True
    
    def delete_all_by_user(self, db: Session, user_id: int) -> int:
        """
        Delete all books for a user (returns count of deleted books)
        """
        count = db.query(Book).filter(Book.user_id == user_id).delete()
        db.commit()
        return count
    
    # ─────────────────────────────────────────────────────────────
    # COUNT & STATISTICS
    # ─────────────────────────────────────────────────────────────
    def count_by_user(self, db: Session, user_id: int) -> int:
        """
        Count total books for a user
        """
        return db.query(Book).filter(Book.user_id == user_id).count()
    
    def count_by_status(self, db: Session, user_id: int, status: str) -> int:
        """
        Count books with specific status for a user
        """
        return db.query(Book).filter(
            Book.user_id == user_id,
            Book.status == status
        ).count()
    
    def get_stats(self, db: Session, user_id: int) -> dict:
        """
        Get reading statistics for a user
        """
        total = self.count_by_user(db, user_id)
        to_read = self.count_by_status(db, user_id, "To Read")
        reading = self.count_by_status(db, user_id, "Reading")
        completed = self.count_by_status(db, user_id, "Completed")
        
        # Genre breakdown
        genre_counts = db.query(
            Book.genre, 
            func.count(Book.id)
        ).filter(
            Book.user_id == user_id
        ).group_by(Book.genre).all()
        
        genres = {genre: count for genre, count in genre_counts}
        
        return {
            "total_books": total,
            "to_read": to_read,
            "reading": reading,
            "completed": completed,
            "genres": genres
        }


# Create a singleton instance
book_repository = BookRepository()