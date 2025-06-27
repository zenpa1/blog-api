from app import models, schemas  # Models and schemas
from fastapi import APIRouter, Depends  # FastAPI-related toolkit
from sqlalchemy.orm import Session  # Database session type hint
from ..auth import hash_password  # Password hashing
from ..database import get_db  # For database sessions

router = APIRouter(prefix="/users", tags=["users"])

# CREATE a user
@router.post("", response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate,  # Pydantic model for request body
    db: Session = Depends(get_db)
    ):

    hashed_password = hash_password(user.password)  # Hash password before storing
    db_user = models.User(
        username = user.username,
        email = user.email,
        password_hash = hashed_password
    )
    db.add(db_user)  # Stage object for insertion
    db.commit()  # Save to database
    db.refresh(db_user)  # Update object with database defaults
    return db_user