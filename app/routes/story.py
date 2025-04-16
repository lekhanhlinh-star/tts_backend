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

@story_router.post("/")
async def add_story(

    title: str = Form(...),
    uid: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    picture: Optional[UploadFile] = File(None),  
    db: Session = Depends(get_db)
):
    logging.info(f"📌 Creating story for UID: {uid}, Title: {title}")

    # Ensure user directories exist
    user_audio_dir = os.path.join(AUDIO_DIR, uid)
    user_image_dir = os.path.join(IMAGE_DIR, uid)
    os.makedirs(user_audio_dir, exist_ok=True)
    os.makedirs(user_image_dir, exist_ok=True)

    # Save image if provided
    picture_path = None
    if picture:
        safe_filename = f"{uid}_{os.path.basename(picture.filename)}"  # Prevent directory traversal
        picture_path = os.path.join(user_image_dir, safe_filename)
        with open(picture_path, "wb") as f:
            f.write(await picture.read())
        logging.info(f"🎨 Image saved at: {picture_path}")

    # Create Story entry with status="process"
    story = Story(title=title, uid=uid, content=content, category=category, picture=picture_path, status="process")
    db.add(story)
    db.commit()
    db.refresh(story)
    logging.info(f"✅ Story {story.story_id} saved with status 'process'")

    # Retrieve user's voice recording
    recording = db.query(VoiceRecording).filter(VoiceRecording.uid == uid).first()
    if not recording or not recording.file_path:
        logging.error("❌ User has no valid voice recording!")
        raise HTTPException(status_code=405, detail="User does not have a valid voice recording")

    speaker_prompt_audio_path = os.path.join(AUDIO_DIR, recording.file_path)
    output_audio_filename = f"{story.story_id}.wav"
    output_audio_path = os.path.join(user_audio_dir, output_audio_filename)

    logging.info(f"🎤 Speaker Prompt Audio: {speaker_prompt_audio_path}")
    logging.info(f"🔄 Output Audio Path: {output_audio_path}")

    # Add background task
    create_story_task.delay(story.story_id, speaker_prompt_audio_path, output_audio_path, content)

    # Return Story object with its details
    return {"message": "Story is being processed in the background", "story": story}

@story_router.get("/{uid}/{storyId}")
async def get_audio_story(uid: str, storyId: str,db: Session = Depends(get_db)):
    return await get_story(uid, storyId,db)

@story_router.get("/status/{uid}/{storyId}")
async def get_status(uid: str, storyId: str,db: Session = Depends(get_db)):
    return await get_status_story(uid, storyId,db)