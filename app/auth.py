# -- Authentication Logic --
from app import models  # Models
import bcrypt  # For hashing passwords
from datetime import datetime, timedelta, timezone  # For access token expiration
from fastapi import Header, Depends, HTTPException, status  # FastAPI-related toolkit
from fastapi.security import OAuth2PasswordBearer  # For auth dependency
import secrets  # For strong randomization of tokens
from sqlalchemy.orm import Session  # Database session type hint
import string  # For API key generation
from typing import Dict  # For api_keys
from .database import get_db  # For database sessions

SECRET_KEY = "secret"  # Preferably in .env file
ALGORITHM = "HS256"  # Symmetric encryption

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Memory storage (stores dict for expiry and user_id) with server-side cleanup
api_keys: Dict[str, dict] = {}

# Hash a password using bcrypt (passlib was initially used but was prone to errors)
def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_password = hashed_password.decode('utf-8')  # Store the hashed password correctly
    return string_password

# Check if the provided password matches the stored password (hashed)
def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf=8')  # Added as a fix
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)

# Generate an API key
def generate_api_key(length: int = 64) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range (length))

# Set expiration
def create_api_key(user_id: int) -> str:
    api_key = generate_api_key()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=5)  # Set five minutes for expiration
    api_keys[api_key] = {"expiry": expiration, "user_id": user_id}
    return api_key

# Validate API key
def validate_api_key(api_key: str) -> bool:
    # If API key does not exist
    if api_key not in api_keys:
        return None
    
    # If API Key is expired
    data = api_keys[api_key]
    if datetime.now(timezone.utc) > data["expiry"]:
        del api_keys[api_key]
        return None
    
    return data["user_id"]

# Authentication dependency
async def get_current_user(
        x_api_token: str = Header(..., alias="X-API-Token"),
        db: Session = Depends(get_db)
) -> models.User:
    # Check if token exists and get user_id
    user_id = validate_api_key(x_api_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Invalid or expired API token."}
        )
    
    # Fetch user from database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "User not found in database."}
        )
    
    return user