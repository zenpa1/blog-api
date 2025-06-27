from app import models  # Models
from fastapi import APIRouter, Depends, HTTPException  # FastAPI-related toolkit
from sqlalchemy.orm import Session  # Database session type hint
from ..auth import verify_password, create_access_token  # For passwords and tokens
from ..database import get_db  # For database sessions

router = APIRouter(tags=["authentication"])

# Finds a user by username
def find_user(username: str, db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.username == username).first()

# LOGIN a user
@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = find_user(username, db)

    # Verify user exists AND password is correct
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials!")
    
    # Generate JWT token
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"} 