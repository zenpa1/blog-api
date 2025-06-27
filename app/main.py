# -- FastAPI Instance and Routes --
from app import models, database  # Models and database functionality
from fastapi import FastAPI  # Core app
from .routers import posts, users, comments, auth  # For including routers

# Create all tables if not existing
models.Base.metadata.create_all(bind=database.engine)
print(f"✅ Database tables created at: {database.DB_URL}")

# Create FastAPI instance
app = FastAPI()

# Setup routers
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(comments.router)
app.include_router(auth.router)
