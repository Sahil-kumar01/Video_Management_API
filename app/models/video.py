from pydantic import BaseModel
from typing import List, Optional

class VideoMetadata(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None