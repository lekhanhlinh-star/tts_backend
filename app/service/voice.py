import uuid
from fastapi import Depends,HTTPException
from datetime import datetime
from fastapi.responses import JSONResponse
from schemas.voice import VoiceCreate
from models.user import User 
from models.VoicePrint import VoicePrint
from models.story import Story
from models.voice import VoiceRecording
from background.tasks import create_story_task
from utils.database import get_db,Session
import os
VOICE_DIR = "voice_files"
os.makedirs(VOICE_DIR, exist_ok=True)

async def create_record_voice(
    uid,
    voice,
    prompt_text,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.uid == uid).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    
    # Thêm bản ghi âm mới
    filename = f"{uid}_{uuid.uuid4()}.wav"
    file_path = os.path.join(VOICE_DIR, filename)

    try:
        with open(file_path, "wb") as f:
            f.write(await voice.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    recording = VoiceRecording(uid=uid, file_path=filename,prompt_text=prompt_text)
    db.add(recording)
    db.commit()
    stories = db.query(Story).all()
    for story in stories:
        voice_print = db.query(VoicePrint).filter(VoicePrint.story_id==story.story_id and VoicePrint.uid==uid).first()
        if not voice_print:
            voice_print = VoicePrint(story_id=story.story_id,uid=uid,status="process")
            db.add(voice_print)
            db.commit()
        else:
            voice_print.status="process"
            db.commit()



    for story in stories:
        voice_print = db.query(VoicePrint).filter(VoicePrint.story_id==story.story_id and VoicePrint.uid==uid).first()
        if not voice_print:
            voice_print = VoicePrint(story_id=story.story_id,uid=uid,status="process")
            db.add(voice_print)
            db.commit()
        create_story_task.delay(voice_print.id,prompt_text)
    
    recording.finished_at = datetime.utcnow()


    return {"status": "success"}


async def check_recording(uid: str, db: Session = Depends(get_db)):
    # check user
    user = db.query(User).filter(User.uid==uid).first()
    if not user:
        return JSONResponse(
            content="User is not exists",
            status_code=404
        )
    voiceprint_count = db.query(VoicePrint).filter(VoicePrint.uid == uid and VoicePrint.status=="finish").count()
    recording = db.query(VoiceRecording).filter(VoiceRecording.uid == uid).order_by(VoiceRecording.created_at.desc()).first()

    total_stories = db.query(Story).count()
    if voiceprint_count >= total_stories:
        return {
        "status": "finish",
        "detail": {"createdAt":  recording.finished_at.isoformat()}
    }
    else:
        return {
            "status": "denial",
            "detail": {"createdAt": ""}
        }

    



