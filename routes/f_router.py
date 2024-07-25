from fastapi import APIRouter, File, UploadFile
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
