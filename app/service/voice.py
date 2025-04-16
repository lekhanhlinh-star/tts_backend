import uuid
from fastapi import Depends,HTTPException
from fastapi.responses import JSONResponse
from schemas.voice import VoiceCreate
from models.user import User 
from models.voice import VoiceRecording
from utils.database import get_db,Session
import os
VOICE_DIR = "app/voice_files"
os.makedirs(VOICE_DIR, exist_ok=True)

async def create_record_voice(
    uid,
    voice,
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

    recording = VoiceRecording(uid=uid, file_path=filename)
    db.add(recording)
    db.commit()

    return {"status": "success"}


async def check_recording(uid: str, db: Session = Depends(get_db)):
    # check user
    user = db.query(User).filter(User.uid==uid).first()
    if not user:
        return JSONResponse(
            content="User is not exists",
            status_code=404
        )
    last_recording = db.query(VoiceRecording).filter(VoiceRecording.uid == uid).order_by(VoiceRecording.created_at.desc()).first()

    if not last_recording:
        return {"status": "denial", "detail": {"createdAt": ""}}

    return {
        "status": "finish",
        "detail": {"createdAt": last_recording.created_at.isoformat()}
    }



