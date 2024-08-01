from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class VideoMetadata(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class VideoResponse(BaseModel):
    filename: str
    id: str  
    title: str
    description: Optional[str] = None
    tags: List[str]
    upload_date: datetime

class DVideoResponse(BaseModel):
    filename: str
    id: str  
    title: str
    description: Optional[str] = None
    tags: List[str]
    deleted_date: datetime

