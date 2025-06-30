# -- Post Router --
from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI-related toolkit
from sqlalchemy.orm import Session  # Database session type hint
from app import models, schemas  # Models and schemas
from ..auth import get_current_user  # For authentication
from ..database import get_db  # For database sessions

router = APIRouter(prefix="/posts", tags=["posts"])  # Add /posts prefix to all routes

# Finds a post by post_id
def find_post(post_id: int, db: Session = Depends(get_db)):
    return db.query(models.Post).filter(models.Post.id == post_id).first()  # Retrieve post

# GET all posts
@router.get("", response_model=list[schemas.PostResponse])
def read_posts(db:Session = Depends(get_db)):
    return db.query(models.Post).all()  # Retrieve all posts

# GET a specific post
@router.get("/{post_id}", response_model=schemas.PostResponse)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = find_post(post_id, db)
    # If post does not exist
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found!"
            )
    return post

# CREATE a post
@router.post("", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post: schemas.PostCreate,  # Pydantic model for request body
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # Requires valid 64-char API token
    ):

    # Create new post
    new_post = models.Post(
        title=post.title,
        content=post.content,
        author_id=current_user.id
    )
    db.add(new_post)  # Stage object for insertion
    db.commit()  # Save to database
    db.refresh(new_post)  # Update object with database defaults
    return new_post

# UPDATE a specific post
@router.patch("/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,  # Pydantic model for request body
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # Requires valid 64-char API token
    ):

    # Find the post
    updated_post = find_post(post_id, db)
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post (id {post_id}) not found!"
        )
    
    # Verify ownership
    if updated_post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are either unauthenticated or you are not using the account that created the post."
        )
    
    # Update fields if provided
    if post_update.title is not None:
        updated_post.title = post_update.title
    if post_update.content is not None:
        updated_post.content = post_update.content

    db.commit()  # Save to database
    db.refresh(updated_post)
    return updated_post

# DELETE a specific post
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # Requires valid 64-char API token
    ):

    # Find the post
    post = find_post(post_id, db)
    if not post:  # Existence check
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post (id {post_id}) not found!"
        )
    
    # Verify ownership
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are either unauthenticated or you are not using the account that created the post."
        )
    db.delete(post)  # Stage object for deletion
    db.commit()  # Save to database
    return None