from fastapi import APIRouter, Depends, HTTPException  # FastAPI-related toolkit
from sqlalchemy.orm import Session  # Database session type hint
from app import models, schemas  # Models and schemas
from ..auth import hash_password, verify_password, create_access_token  # For passwords and tokens
from ..database import get_db  # For database sessions

router = APIRouter(prefix="/users", tags=["users"])

# Finds a user by username
def find_user(username: str, db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.username == username).first()

# CREATE a user
@router.post("/", response_model=schemas.UserResponse)
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