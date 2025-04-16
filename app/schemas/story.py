from pydantic import BaseModel
from typing import Optional, Dict, Union
from fastapi import File,UploadFile

class StoryCreate(BaseModel):
    title: str
    uid: str
    content: str
    picture :UploadFile =File(...)
    
class StoryStatusResponse(BaseModel):
    status: str
    detail: Optional[Dict] = None