# -- Post Router --
from fastapi import APIRouter, Depends, HTTPException, status, Query  # FastAPI-related toolkit
from sqlalchemy import or_  # For OR conditions in filtering
from sqlalchemy.orm import Session  # Database session type hint
from app import models, schemas  # Models and schemas
from typing import Optional  # For optional search query
from ..auth import get_current_user  # For authentication
from ..database import get_db  # For database sessions

# [Testing] To create fake data
from faker import Faker

router = APIRouter(prefix="/posts", tags=["posts"])

# Finds a post by post_id
def find_post(post_id: int, db: Session = Depends(get_db)):
    return db.query(models.Post).filter(models.Post.id == post_id).first()  # Retrieve post

# GET all posts
@router.get("", response_model=list[schemas.PostResponse])
def read_posts(
    db:Session = Depends(get_db),
    page: int = Query(1, gt=0),  # Default page is 1, must be > than 0
    take: int = Query(25, gt=0),  # Default items shown is 25, must be > than 0
    search: Optional[str] = Query(None)  # Optional for searching
    ):
    
    # Start with base query
    query = db.query(models.Post)

    # Apply filtering
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            # Two possible conditions
            or_(
                models.Post.title.ilike(search_term),
                models.Post.content.ilike(search_term)
            )
        )

    # Apply pagination (offset skips the first N records [page 1: skip 0, page 2: skip 25], limit takes only the specified number of records)
    posts = query.order_by(models.Post.created_at.desc()).offset((page - 1) * take).limit(take).all()
    return posts

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
            detail=f"Post with id {post_id} not found!"
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
@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # Requires valid 64-char API token
    ):

    # Find the post
    post = find_post(post_id, db)
    if not post:  # Existence check
        return {"success": False, "message": f"Post with id {post_id} not found!"}
    
    # Verify ownership
    if post.author_id != current_user.id:
        return {"success": False, "message": "You are either unauthenticated or you are not using the account that created the post."}

    db.delete(post)  # Stage object for deletion
    db.commit()  # Save to database
    return {"success": True}

# [Testing] To test pagination
@router.post("/generate-test-posts")
def generate_test_posts(
    count: int = 100,  # Number of posts to generate
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    fake = Faker()
    posts = []
    
    for _ in range(count):
        post = models.Post(
            title=fake.sentence(nb_words=6),
            content=fake.text(max_nb_chars=200),
            author_id=current_user.id
        )
        posts.append(post)
    
    db.add_all(posts)
    db.commit()
    return {"message": f"Generated {count} test posts"}