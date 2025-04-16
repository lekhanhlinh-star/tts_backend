from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import os

# Load environment variables
load_dotenv()

# Security - Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Create database engine
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=0, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

# Utility functions for password hashing
def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against a hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

# Dependency to get the database session
def get_db():
    """Yields a new database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
