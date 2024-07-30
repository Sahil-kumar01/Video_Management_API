import shutil
from fastapi import UploadFile
import os

async def save_file(file: UploadFile):
    file_path = os.path.join('videos', file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path

async def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
