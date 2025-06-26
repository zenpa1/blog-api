# -- SQLite Database Connector --
from pathlib import Path  # For custom paths
from sqlalchemy import create_engine  # For initializing engine
from sqlalchemy.ext.declarative import declarative_base  # For models
from sqlalchemy.orm import sessionmaker  # For sessions

# Custom path for database
DB_PATH = Path(__file__).parent / "data" / "blog.db"

# Create folder for database if it does not exist
DB_PATH.parent.mkdir(exist_ok=True)

# SQLite database file
DB_URL = f"sqlite:///{DB_PATH}"

# Create an engine to manage connections to database
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False}  # Enable multiple threads for FastAPI
)

# Session factory for creating individual sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Setup database session
def get_db():
    db = SessionLocal()
    try:
        yield db  # Deliver session to route
    finally:
        db.close()  # Ensure session closes after request