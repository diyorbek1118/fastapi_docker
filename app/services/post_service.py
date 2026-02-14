"""
Post Service - ASYNC version
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.post import Post
from schemas.post import PostCreate
from core.exceptions import (
    PostNotFoundException,
    DatabaseException
)
import logging

logger = logging.getLogger(__name__)


# ========================================
# CREATE POST
# ========================================
async def create_post(db: AsyncSession, post: PostCreate) -> Post:
    """
    Create a new post (ASYNC).
    
    Args:
        db: Async database session
        post: Post data
        
    Returns:
        Created post
        
    Raises:
        DatabaseException: If database error occurs
    """
    try:
        # 1. Create post instance
        db_post = Post(**post.model_dump())
        
        # 2. Add to session
        db.add(db_post)
        
        # 3. Commit (ASYNC!)
        await db.commit()
        
        # 4. Refresh to get ID (ASYNC!)
        await db.refresh(db_post)
        
        logger.info(f"Post created successfully: ID={db_post.id}")
        return db_post
        
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error creating post: {str(e)}")
        raise DatabaseException("Could not create post: Integrity constraint violated")
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error creating post: {str(e)}")
        raise DatabaseException("Database error occurred while creating post")


# ========================================
# GET POST BY ID
# ========================================
async def get_post(db: AsyncSession, post_id: int) -> Post:
    """
    Get post by ID (ASYNC).
    
    Args:
        db: Async database session
        post_id: Post ID
        
    Returns:
        Post object
        
    Raises:
        PostNotFoundException: If post not found
    """
    # Modern SQLAlchemy 2.0 syntax
    result = await db.execute(
        select(Post).where(Post.id == post_id)
    )
    
    db_post = result.scalar_one_or_none()
    
    if db_post is None:
        logger.warning(f"Post not found: ID={post_id}")
        raise PostNotFoundException(post_id)
    
    return db_post


# ========================================
# GET ALL POSTS
# ========================================
async def get_posts(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Get all posts with pagination (ASYNC).
    
    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of posts
    """
    try:
        # Modern syntax with select()
        result = await db.execute(
            select(Post)
            .offset(skip)
            .limit(limit)
        )
        
        # Get all results
        posts = result.scalars().all()
        
        return posts
        
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching posts: {str(e)}")
        raise DatabaseException("Could not fetch posts")


# ========================================
# DELETE POST
# ========================================
async def delete_post(db: AsyncSession, post_id: int) -> bool:
    """
    Delete post by ID (ASYNC).
    
    Args:
        db: Async database session
        post_id: Post ID
        
    Returns:
        True if deleted
        
    Raises:
        PostNotFoundException: If post not found
        DatabaseException: If database error occurs
    """
    # Get post (raises exception if not found)
    db_post = await get_post(db, post_id)
    
    try:
        # Delete
        await db.delete(db_post)
        
        # Commit (ASYNC!)
        await db.commit()
        
        logger.info(f"Post deleted successfully: ID={post_id}")
        return True
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error deleting post: {str(e)}")
        raise DatabaseException("Could not delete post")


# ========================================
# COMPARISON: OLD vs NEW
# ========================================
"""
OLD (Sync):
    posts = db.query(Post).all()

NEW (Async):
    result = await db.execute(select(Post))
    posts = result.scalars().all()

Key differences:
1. await keyword
2. execute() instead of query()
3. select() instead of query builder
4. scalars().all() to get results
"""