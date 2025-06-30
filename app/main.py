# -- FastAPI Instance and Routes --
from app import models, database  # Models and database functionality
from fastapi import FastAPI  # Core app
from fastapi.middleware.cors import CORSMiddleware  # For CORS
from .routers import posts, users, comments, auth  # For including routers

# Create all tables if not existing
models.Base.metadata.create_all(bind=database.engine)
print(f"✅ Database tables created at: {database.DB_URL}")

# Create FastAPI instance
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,  # CORS configuration
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  # List of allowed URLs
    allow_credentials=True,  # Allows cookies and authentication headers
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"]  # Accepts all request headers
)

# Setup routers
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(comments.router)
app.include_router(auth.router)