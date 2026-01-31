from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.post import Post
from schemas.post import PostCreate, PostResponse
from services.post_service import create_post

router = APIRouter(prefix="/posts", tags=["Posts"])

# DB session yaratish
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=PostResponse)
def create_post_endpoint(post: PostCreate, db: Session = Depends(get_db)):
    return create_post(db=db, post=post)
