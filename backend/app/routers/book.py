from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Book(Base):
    """
    Book table - stores book entries for reading tracker
    """
    
    # Table name in database
    __tablename__ = "books"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    genre = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String(20), default="To Read", nullable=False)
    notes = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship - Book belongs to one User
    owner = relationship("User", back_populates="books")
    
    def __repr__(self):
        return f"<Book(id={self.id}, title={self.title}, author={self.author}, status={self.status})>"