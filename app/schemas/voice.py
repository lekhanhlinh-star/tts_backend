from pydantic import BaseModel
from typing import Optional, Dict, Union
from fastapi import UploadFile, File, Form


class VoiceCreate(BaseModel):
    uid: str = Form(...)
    voice: UploadFile = File(...)

class StoryStatusResponse(BaseModel):
    status: str
    detail: Optional[Dict] = None