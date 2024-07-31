from fastapi import APIRouter, File, UploadFile, HTTPException,Form,status,Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import shutil
from app.services.video import save_video_metadata,get_video_by_id,update_video_metadata,delete_video_by_id
from app.models.video import VideoMetadata
from app.check_types import ALLOWED_MIME_TYPES
router = APIRouter()

os.makedirs('videos', exist_ok=True)

@router.post("/upload-video/")
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: List[str] = Form(...)
):
   
    
    # check if the uploaded file is in an allowed video format
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
    return {"filename": file.filename, "id": video_id}

@router.get("/get-video/{video_id}")
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


@router.put("/update-metadata/{video_id}")
async def update_metadata(video_id: str, metadata: VideoMetadata):
    try:
        matched_count = await update_video_metadata(video_id, metadata.dict())
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid video ID format")
    
    if matched_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {"message": "Metadata updated successfully"}

@router.delete("/delete-video/{video_id}")
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
    return {"message": "Video and metadata deleted successfully"}
