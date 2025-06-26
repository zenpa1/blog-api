# -- JWT Authentication Logic --
from app import models  # Models
import bcrypt  # For hashing passwords
from datetime import datetime, timedelta, timezone  # For access token expiration
from fastapi import Depends, HTTPException, status  # FastAPI's dependency injection system
from fastapi.security import OAuth2PasswordBearer  # For auth dependency
from jose import jwt, JWTError  # For access tokens
from sqlalchemy.orm import Session  # Database session type hint
from .database import get_db  # For database sessions

SECRET_KEY = "secret"  # Preferably in .env file
ALGORITHM = "HS256"  # Symmetric encryption

# Login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# Hash a password using bcrypt (passlib was initially used but was prone to errors)
def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_password = hashed_password.decode('utf-8')  # Store the has password correctly
    return string_password

# Check if the provided password matches the stored password (hashed)
def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf=8')  # Added as a fix
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)

# Creates an access token with python-jose[cryptography]
def create_access_token(data: dict) -> str:
    to_encode = data.copy()  # Avoid mutating original data
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)  # Expires in five minutes
    to_encode.update({"exp": expire})  # Add expiration time
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Generate JWT

# Checks for valid JWT and verifies if post owner matches logged-in user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user!")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token!")