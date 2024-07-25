from fastapi import APIRouter, File, UploadFile,HTTPException
from fastapi.responses import FileResponse
import shutil
import os


router = APIRouter()

# Ensure the directory exists
os.makedirs('videos', exist_ok=True)

@router.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join('videos', file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@router.get("/get-video/{filename}")
async def get_video(filename: str):
    file_path = os.path.join('videos',filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code = 404,detail = "video not found")
    return FileResponse(file_path)

