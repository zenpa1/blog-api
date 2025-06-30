# -- Authentication Router --
from app import models  # Models
from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI-related toolkit
from sqlalchemy.orm import Session  # Database session type hint
from ..auth import verify_password, create_api_key  # For passwords and tokens
from ..database import get_db  # For database sessions

router = APIRouter(tags=["authentication"])

# Finds a user by username
def find_user(username: str, db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.username == username).first()

# LOGIN a user
@router.post("/login")
def login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
    ):
    
    user = find_user(username, db)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Invalid credentials!"}
        )
    
    # Generate 64-character API key that expires in 5 minutes
    api_key = create_api_key(user.id)
    return {
        "api_key": api_key,
        "expires_in": "5 minutes",
        "success": True
    }