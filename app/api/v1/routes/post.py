from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.redis_client import redis_client
import json

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
@router.get("/")
def get_posts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all posts with cache"""
    
    # Cache key
    cache_key = f"posts:{skip}:{limit}"
    
    # Try cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Get from DB
    if limit > 100:
        limit = 100
    posts = post_service.get_posts(db=db, skip=skip, limit=limit)
    
    # Convert to dict
    posts_data = [
        {"id": p.id, "title": p.title, "content": p.content}
        for p in posts
    ]
    
    # Save to cache (60s)
    redis_client.set(cache_key, json.dumps(posts_data), ex=60)
    
    return posts_data


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