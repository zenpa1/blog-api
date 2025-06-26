# -- SQLAlchemy Models --
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey  # Columns
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base  # Base component

# Define a User table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)  # Store hashed passwords

    # Relationship to posts
    posts = relationship("Post", back_populates="owner")

# Define a Post table
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to user
    owner = relationship("User", back_populates="posts")

    # Relationship to comments
    comments = relationship("Comment", back_populates="post")

# Define a Comment table
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    body = Column(String)
    commenter_name = Column(String)
    post_id = Column(Integer, ForeignKey("posts.id"))

    # Relationship to post
    post = relationship("Post", back_populates="comments")