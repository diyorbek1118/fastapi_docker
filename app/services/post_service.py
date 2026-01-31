from sqlalchemy.orm import Session
from models.post import Post
from schemas.post import PostCreate

def create_post(db: Session, post: PostCreate):
    db_post = Post(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
