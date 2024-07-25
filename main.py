from fastapi import FastAPI,UploadFile,File
import shutil
import os
app = FastAPI()

os.makedirs('videos',exist_ok = True)
@app.post("/upload_video")
async def upload_video(file:UploadFile= File(...)):
    file_path = os.path.join('videos',file.filename)
    with open(file_path,'wb') as buffer:
        shutil.copyfileobj(file.file,buffer)
    return {"filename":file.filename}
