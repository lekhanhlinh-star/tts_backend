from service.voice import check_recording, create_record_voice
from utils.database import get_db,Session
from schemas.voice import VoiceCreate
from fastapi import APIRouter,Depends,File,Form,UploadFile


voice_router = APIRouter(prefix="/api/v1/voice")

@voice_router.post("/")
async def upload_recording(uid:str=Form(...),
                           voice:UploadFile=File(...),
                           prompt_text:str =Form(...),
                            db: Session = Depends(get_db)):
    return await create_record_voice(uid,voice,prompt_text,db)


# @voice_router.get("/story-recordings/{story_id}")

# API 5 confirms whether the user has recorded a video

@voice_router.get("/user/{uid}")
async def check_voice_by_user(uid:str,db: Session = Depends(get_db)):
    return await check_recording(uid,db)


