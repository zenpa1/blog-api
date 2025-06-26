# -- FastAPI Instance and Routes --
from fastapi import FastAPI  # Core app
from app import models, database  # SQLAlchemy table definitions and database functionality
from .routers import posts, users, comments  # For including routers

# Create all tables if not existing
models.Base.metadata.create_all(bind=database.engine)
print(f"✅ Database tables created at: {database.DB_URL}")

# Create FastAPI instance
app = FastAPI()

# Setup routers
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(comments.router)

# Handle dependencies

# Add security
