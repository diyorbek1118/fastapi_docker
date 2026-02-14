"""
Post Routes - ASYNC version
"""
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.redis_client import redis_client
import json

from core.dependencies import get_async_db, get_authenticated_user
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
async def get_posts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)  # ← ASYNC!
):
    """
    Get all posts with cache (ASYNC).
    
    Performance: 3-5x faster than sync version
    """
    
    # Cache key
    cache_key = f"posts:{skip}:{limit}"
    
    # Try cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Get from DB (ASYNC!)
    if limit > 100:
        limit = 100
    
    posts = await post_service.get_posts(db=db, skip=skip, limit=limit)  # ← await!
    
    # Convert to dict
    posts_data = [
        {"id": p.id, "title": p.title, "content": p.content}
        for p in posts
    ]
    
    # Save to cache (60s)
    redis_client.set(cache_key, json.dumps(posts_data), ex=60)
    
    return posts_data


@router.get("/{post_id}")
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get single post by ID (ASYNC).
    """
    post = await post_service.get_post(db=db, post_id=post_id)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content
    }


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
async def create_post(
    request: Request,
    post: PostCreate,
    current_user: User = Depends(get_authenticated_user),  # Sync (hozircha)
    db: AsyncSession = Depends(get_async_db)  # ASYNC!
):
    """
    Create a new post (requires authentication).
    Rate limit: 10 posts per minute.
    
    ASYNC version - faster response time
    """
    created_post = await post_service.create_post(db=db, post=post)  # ← await!
    return created_post


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete post (Login kerak)"
)
@limiter.limit("20/minute")
async def delete_post(
    request: Request,
    post_id: int,
    current_user: User = Depends(get_authenticated_user),  # Sync (hozircha)
    db: AsyncSession = Depends(get_async_db)  # ASYNC!
):
    """
    Delete a post (requires authentication).
    Rate limit: 20 deletions per minute.
    
    ASYNC version
    """
    await post_service.delete_post(db=db, post_id=post_id)  # ← await!
    return None


# ========================================
# NOTES
# ========================================
"""
Key changes:
1. async def instead of def
2. AsyncSession instead of Session
3. get_async_db instead of get_db
4. await service calls

Auth hozircha sync (keyinroq async qilamiz)
"""