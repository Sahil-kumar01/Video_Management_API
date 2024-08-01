from fastapi import APIRouter, File, UploadFile, HTTPException,Form,status,Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import shutil
from app.services.video import save_video_metadata,get_video_by_id,update_video_metadata,delete_video_by_id,get_videos_by_tag
from app.models.video import VideoMetadata,VideoResponse,DVideoResponse
from app.check_types import ALLOWED_MIME_TYPES
router = APIRouter()

os.makedirs('videos', exist_ok=True)



@router.post("/video", response_model=VideoResponse, tags=["Video Management"],description="The post method is used to upload the video files into the database.")
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: List[str] = Form(...)
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format: {file.content_type}. Please upload a video file."
        )

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
    
    video_id = await save_video_metadata(video_data)
    
    return {
        "filename": file.filename,
        "id": video_id,
        "title": title,
        "description": description,
        "tags": tags,
        "upload_date": video_data["upload_date"]
    }



@router.get("/video",response_model=VideoResponse,tags=["Video Management"])
async def get_video(video_id: str):
    try:
        video = await get_video_by_id(video_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid video ID format")
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_path = video["path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(file_path)
   


@router.get("/videos/findByTags",tags=["Video Management"])
async def search_videos_by_tag(tag: str):
    videos = await get_videos_by_tag(tag)
    if not videos:
        raise HTTPException(status_code=404, detail="No videos found with the specified tag")
    return videos




@router.put("/video",tags=["Video Management"])
async def update_metadata(video_id: str, metadata: VideoMetadata):
    try:
        matched_count = await update_video_metadata(video_id, metadata.dict())
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid video ID format")
    
    if matched_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {"message": "Metadata updated successfully"}



@router.delete("/video",response_model=DVideoResponse,tags=["Video Management"])
async def delete_video(video_id: str):
    try:
        video = await get_video_by_id(video_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid video ID format")
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_path = video.get("path")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
    
    await delete_video_by_id(video_id)
    
    response = DVideoResponse(
        filename=video["filename"],
        id=video_id,
        title=video["title"],
        description=video.get("description"),
        tags=video.get("tags", []),
        deleted_date=datetime.now()
    )
    
    return response 