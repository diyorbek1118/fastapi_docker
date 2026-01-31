# app/main.py
from fastapi import FastAPI
from core.database import Base, engine
from models.post import Post  # Post modelini import qilamiz
from api.v1.routes import post

# Table’larni yaratish
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Docker Project")
app.include_router(post.router)
