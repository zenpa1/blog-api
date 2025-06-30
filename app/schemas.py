# -- Pydantic Models for Request/Response Validation --
from datetime import datetime  # For created_at
from pydantic import BaseModel, EmailStr, Field, model_validator  # For models
from typing import Optional  # Optional fields like updating one attribute only

# ---- User Schemas ----
class UserBase(BaseModel):
    username: str = Field(..., example="alice")
    email: EmailStr = Field(..., example="alice@example.com")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="secret123")

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy to Pydantic

# ---- Comment Schemas ----
class CommentBase(BaseModel):
    body: str

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    post_id: int
    commenter: UserResponse  # Nested user data for future usage
    class Config:
        from_attributes = True

class CommentUpdate(BaseModel):
    body: Optional[str] = None

    # At least one field should be provided
    @model_validator(mode="before")
    def at_least_one_field(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be changed!")
        return values

# ---- Post Schemas ----
class PostBase(BaseModel):
    title: str = Field(..., example="My First Post")
    content: str = Field(..., example="Hello world!")

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    created_at: datetime
    author: UserResponse  # Nested user data for future usage
    comments: list[CommentResponse] = []
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy to Pydantic

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

    # At least one field should be provided
    @model_validator(mode="before")
    def at_least_one_field(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be changed!")
        return values
    
# --- Token Schemas ---
class TokenResponse(BaseModel):
    api_key: str
    expires_in: str
    success: bool