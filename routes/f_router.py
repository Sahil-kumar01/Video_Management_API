from fastapi import APIRouter, File, UploadFile, HTTPException,Depends,Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from config import mongo_url
from typing import Optional,List
from datetime import datetime
import shutil
import os

router = APIRouter()

client = AsyncIOMotorClient(mongo_url)
db = client.videos
videos_collection = db.videos

# Ensure the directory exists
os.makedirs('videos', exist_ok=True)

#define pydantic models
class VideoMetadata(BaseModel):
    title :str
    description: Optional[str] = Form(None),
    tags: Optional[List[str]] = Form([])

class VideoInDB(BaseModel):
    id :str
    file_path : str
    upload_date : datetime


@router.post("/upload-video/")
async def upload_video(file: UploadFile = File(...),  metadata : VideoMetadata = Depends()):
    file_path = os.path.join('videos', file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    #store video in metadata form
    video_data = {
        "title": metadata.title,
        "description":metadata.description,
        "tags":metadata.tags,
        "filename":file.filename,
        "path": file_path,
        "upload_date" : datetime.now()

    }
    
    # Store in MongoDB
    # video_data = {"filename": file.filename, "path": file_path}
    result = await videos_collection.insert_one(video_data) 
     # Use insert_one for a single document
    return {"filename":file.filename,"id":str(result.inserted_id)}

    

@router.get("/get-video/{video_id}")
async def get_video(video_id: str):
    video = await videos_collection.find_one({"_id": video_id})
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_path = video["path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(file_path)

@router.put("/update-metadata/{video_id}")
async def update_metadata(video_id:str ,metadata: VideoMetadata):
    result  = await videos_collection.update_one(
        {"_id":video_id},
         {"$set":{
          
             "title": metadata.title,
             "description": metadata.description,
             "tags": metadata.tags
        }}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {"message":"Metadata updated successfully"}

@router.delete("/delete-video/{video_id}")
async def delete_video(video_id:str):
    video = await videos_collection.find_one({"_id":video_id})

    if not video:
        raise HTTPException(status_code = 404, detail = "Video not found")

    file_path = video["path"]
    if os.path.exists(file_path):
        os.remove(file_path)


    await videos_collection.delete_one({"_id":video_id})
    return {"message":"Video deleted successfully"}

    