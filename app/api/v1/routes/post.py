from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db, get_authenticated_user
from schemas.post import PostCreate, PostResponse
from services import post_service
from models.user import User

router = APIRouter(prefix="/posts", tags=["Posts"])


# ========================================
# PUBLIC ENDPOINTS (Token kerak emas)
# ========================================
@router.get(
    "/",
    response_model=List[PostResponse],
    summary="Get all posts"
)
def get_posts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all posts"""
    if limit > 100:
        limit = 100
    return post_service.get_posts(db=db, skip=skip, limit=limit)


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get post by ID"
)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get a post by ID"""
    return post_service.get_post(db=db, post_id=post_id)


# ========================================
# PROTECTED ENDPOINTS (Token kerak!)
# ========================================
@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create post (Login kerak)"
)
def create_post(
    post: PostCreate,
    current_user: User = Depends(get_authenticated_user),  # ← Protected!
    db: Session = Depends(get_db)
):
    """Create a new post (requires authentication)"""
    return post_service.create_post(db=db, post=post)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete post (Login kerak)"
)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_authenticated_user),  # ← Protected!
    db: Session = Depends(get_db)
):
    """Delete a post (requires authentication)"""
    post_service.delete_post(db=db, post_id=post_id)
    return None