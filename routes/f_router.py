from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from config import mongo_url
import shutil
import os

router = APIRouter()

client = AsyncIOMotorClient(mongo_url)
db = client.videos
videos_collection = db.videos

# Ensure the directory exists
os.makedirs('videos', exist_ok=True)

@router.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join('videos', file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Store in MongoDB
    video_data = {"filename": file.filename, "path": file_path}
    await videos_collection.insert_one(video_data)  # Use insert_one for a single document

    return {"filename": file.filename}

@router.get("/get-video/{filename}")
async def get_video(filename: str):
    video = await videos_collection.find_one({"filename": filename})
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_path = video["path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(file_path)
