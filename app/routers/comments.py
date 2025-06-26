from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from ..database import get_db

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])

@router.post("/", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db)
):
    
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found!"
        )
    
    new_comment = models.Comment(
        body=comment.body,
        commenter_name=comment.commenter_name,
        post_id=post_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/", response_model=list[schemas.CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()