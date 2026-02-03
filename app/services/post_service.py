from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models.post import Post
from schemas.post import PostCreate
from core.exceptions import (
    PostNotFoundException,
    DatabaseException
)
import logging

logger = logging.getLogger(__name__)


def create_post(db: Session, post: PostCreate) -> Post:
    """
    Create a new post.
    
    Args:
        db: Database session
        post: Post data
        
    Returns:
        Created post
        
    Raises:
        DatabaseException: If database error occurs
    """
    try:
        db_post = Post(**post.model_dump())
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        logger.info(f"Post created successfully: ID={db_post.id}")
        return db_post
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating post: {str(e)}")
        raise DatabaseException("Could not create post: Integrity constraint violated")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating post: {str(e)}")
        raise DatabaseException("Database error occurred while creating post")


def get_post(db: Session, post_id: int) -> Post:
    """
    Get post by ID.
    
    Args:
        db: Database session
        post_id: Post ID
        
    Returns:
        Post object
        
    Raises:
        PostNotFoundException: If post not found
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()
    
    if db_post is None:
        logger.warning(f"Post not found: ID={post_id}")
        raise PostNotFoundException(post_id)
    
    return db_post


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all posts with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of posts
    """
    try:
        return db.query(Post).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching posts: {str(e)}")
        raise DatabaseException("Could not fetch posts")


def delete_post(db: Session, post_id: int) -> bool:
    """
    Delete post by ID.
    
    Args:
        db: Database session
        post_id: Post ID
        
    Returns:
        True if deleted
        
    Raises:
        PostNotFoundException: If post not found
        DatabaseException: If database error occurs
    """
    db_post = get_post(db, post_id)  # Raises PostNotFoundException if not found
    
    try:
        db.delete(db_post)
        db.commit()
        logger.info(f"Post deleted successfully: ID={post_id}")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting post: {str(e)}")
        raise DatabaseException("Could not delete post")