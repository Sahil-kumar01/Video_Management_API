from fastapi import FastAPI
from app.routers import video

app = FastAPI()

app.include_router(video.router, prefix="/videos")
