from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from .env file
    """
    
    # App Settings
    APP_NAME: str = "Book Buddy"
    DEBUG: bool = True
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./book_buddy.db"
    
    # JWT Settings
    SECRET_KEY: str = "your-super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"


# Create settings instance
settings = Settings()