from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from passlib.context import CryptContext
import os

# Database Configuration
Base = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

# Remove optional quotes and spaces from .env value
DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'")

# Create SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Password Hash Configuration
pwd_context = CryptContext(schemes=["bcrypt", "argon2", "pbkdf2_sha256"])


# Database Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)


# Database Utilities
def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Provide a new database session per request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password Utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)