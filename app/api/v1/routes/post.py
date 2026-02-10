from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.dependencies import get_db, get_authenticated_user
from schemas.post import PostCreate, PostResponse
from services import post_service
from models.user import User

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

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
    """Get all posts - No limit"""
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
    """Get a post by ID - No limit"""
    return post_service.get_post(db=db, post_id=post_id)


# ========================================
# PROTECTED ENDPOINTS (Token kerak + Rate limit)
# ========================================
@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create post (Login kerak)"
)
@limiter.limit("10/minute")
def create_post(
    request: Request,
    post: PostCreate,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Create a new post (requires authentication).
    Rate limit: 10 posts per minute.
    """
    return post_service.create_post(db=db, post=post)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete post (Login kerak)"
)
@limiter.limit("20/minute")
def delete_post(
    request: Request,
    post_id: int,
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Delete a post (requires authentication).
    Rate limit: 20 deletions per minute.
    """
    post_service.delete_post(db=db, post_id=post_id)
    return None