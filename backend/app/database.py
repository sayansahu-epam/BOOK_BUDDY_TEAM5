from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings


# Create SQLite Engine
# connect_args={"check_same_thread": False} is needed only for SQLite
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base Class for Models
Base = declarative_base()


# Dependency to get database session
def get_db():
    """
    Creates a new database session for each request.
    Closes the session after request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()