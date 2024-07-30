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


client = AsyncIOMotorClient(mongo_url)
db = client.videos
videos_collection = db.videos


os.makedirs('videos', exist_ok=True)


class VideoMetadata(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None


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


from bson import ObjectId

@router.get("/get-video/{video_id}")
async def get_video(video_id: str):
    try:
        video = await videos_collection.find_one({"_id": ObjectId(video_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid video ID format")
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_path = video["path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(file_path)



from bson import ObjectId

@router.put("/update-metadata/{video_id}")
async def update_metadata(video_id: str, metadata: VideoMetadata):
    try:
        result = await videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {
                "title": metadata.title,
                "description": metadata.description,
                "tags": metadata.tags
            }}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid video ID format")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {"message": "Metadata updated successfully"}


@router.delete("/delete-video/{video_id}")
async def delete_video(video_id: str):
    try:
        video = await videos_collection.find_one({"_id": ObjectId(video_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid video ID format")
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_path = video["path"]
    if os.path.exists(file_path):
        os.remove(file_path)
    
    await videos_collection.delete_one({"_id": ObjectId(video_id)})
    return {"message": "Video and metadata deleted successfully"}
