from fastapi import APIRouter
from typing import List

router = APIRouter(prefix="/posts", tags=["Posts v2"])

@router.get("/")
def get_posts_v2():
    """v2 - Yangi format"""
    return {
        "version": "v2",
        "data": [
            {
                "id": 1,
                "title": "Post 1",
                "content": "Content",
                "category": "tech",  # ← v2 da yangi!
                "views": 100         # ← v2 da yangi!
            }
        ]
    }