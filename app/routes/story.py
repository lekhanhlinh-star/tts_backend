import logging
import os
from fastapi import APIRouter, Depends, Form, File, UploadFile, BackgroundTasks, HTTPException
from typing import Optional
from utils.database import Session, get_db
from models.story import Story
from service.story import get_story, get_status_story
from models.voice import VoiceRecording
from background.tasks import create_story_task
from models.user import User
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
AUDIO_DIR =  "/app/app/voice_files"
story_router = APIRouter(prefix="/api/v1/story")

@story_router.get("/{uid}/{storyId}")
async def get_audio_story(uid: str, storyId: str,db: Session = Depends(get_db)):
    return await get_story(uid, storyId,db)

@story_router.get("/status/{uid}/{storyId}")
async def get_status(uid: str, storyId: str,db: Session = Depends(get_db)):
    return await get_status_story(uid, storyId,db)