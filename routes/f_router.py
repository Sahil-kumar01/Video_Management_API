from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from config import mongo_url
import shutil
import os
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# MongoDB setup
client = AsyncIOMotorClient(mongo_url)
db = client.videos
videos_collection = db.videos

# Ensure the directory exists
os.makedirs('videos', exist_ok=True)

# Define Pydantic models for video metadata
class VideoMetadata(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None

# Upload video endpoint
@router.post("/upload-video/")
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: List[str] = Form(...)
):
    file_path = os.path.join('videos', file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Store video metadata in MongoDB
    video_data = {
        "title": title,
        "description": description,
        "tags": tags,
        "filename": file.filename,
        "path": file_path,
        "upload_date": datetime.now()
    }
    result = await videos_collection.insert_one(video_data)

    return {"filename": file.filename, "id": str(result.inserted_id)}

# Retrieve video metadata and file
@router.get("/get-video/{video_id}")
async def get_video(video_id: str):
    video = await videos_collection.find_one({"_id": video_id})
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_path = video["path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(file_path)

# Update video metadata
@router.put("/update-metadata/{video_id}")
async def update_metadata(video_id: str, metadata: VideoMetadata):
    result = await videos_collection.update_one(
        {"_id": video_id},
        {"$set": {
            "title": metadata.title,
            "description": metadata.description,
            "tags": metadata.tags
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {"message": "Metadata updated successfully"}

# Delete video and metadata
@router.delete("/delete-video/{video_id}")
async def delete_video(video_id: str):
    video = await videos_collection.find_one({"_id": video_id})
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_path = video["path"]
    if os.path.exists(file_path):
        os.remove(file_path)
    
    await videos_collection.delete_one({"_id": video_id})
    return {"message": "Video and metadata deleted successfully"}
