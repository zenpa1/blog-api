# -- Comment Router --
from app import models, schemas  # Models and schemas
from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI-related toolkit
from sqlalchemy.orm import Session  # Database session type hint
from ..auth import get_current_user  # For authentication
from ..database import get_db  # For database sessions

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])

# Finds a post by post_id
def find_post(post_id: int, db: Session = Depends(get_db)):
    return db.query(models.Post).filter(models.Post.id == post_id).first()  # Retrieve post

# Finds a comment by comment_id
def find_comment(comment_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()  # Retrieve comment

# GET all comments
@router.get("", response_model=list[schemas.CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()

# CREATE a comment
@router.post("", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # Requires valid 64-char API token
    ):
    
    # Check if post exists
    db_post = find_post(post_id, db)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found!"
        )
    
    new_comment = models.Comment(
        body=comment.body,
        post_id=post_id,
        commenter_id=current_user.id
    )

    db.add(new_comment)  # Stage object for insertion
    db.commit()  # Save to database
    db.refresh(new_comment)  # Update object with database defaults
    return new_comment

# UPDATE a comment
@router.patch("/{comment_id}", response_model=schemas.CommentResponse)
def update_comment(
    comment_id: int,
    comment_update: schemas.CommentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    
    # Check if comment exists
    db_comment = find_comment(comment_id, db)
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found!"
        )
    
    # Verify ownership
    if db_comment.commenter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are either unauthenticated or you are not using the account that created the comment."
        )
    
    # Update fields if provided
    if comment_update.body is not None:
        db_comment.body = comment_update.body

    db.commit()  # Save to database
    db.refresh(db_comment)
    return db_comment

# DELETE a comment
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    
    # Check if comment exists
    db_comment = find_comment(comment_id, db)
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found!"
        )
    
    # Verify ownership
    if db_comment.commenter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are either unauthenticated or you are not using the account that created the comment."
        )
    
    db.delete(db_comment)  # Stage object for deletion
    db.commit()  # Save to database
    return None  # Return