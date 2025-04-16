from utils.database import Session,get_db
from utils.zero_shot_tts import ZeroShotTts
from models.voice import VoiceRecording
from models.story import Story
from models.user import User
import os
from schemas.story import StoryCreate
from .voice import VOICE_DIR
from fastapi import Depends, HTTPException,UploadFile,File

from fastapi.responses import FileResponse,JSONResponse





async def create_story(title:str,  uid:str, content:str,  category:str,picture:UploadFile,db: Session = Depends(get_db)):
    existing_story = db.query(Story).filter(Story.title == title and User.uid==uid).first()
    if existing_story:
        raise HTTPException(status_code=400, detail="Story title already exists")
    existing_user = db.query(User).filter(User.uid==uid).first()
    if not existing_user:
        raise HTTPException(status_code=404,detail="User does not exist")
    if picture:
        print(f"Uploaded file: {picture.filename}")
        # You can save the file like this:
        file_path = f"uploads/{picture.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await picture.read())
    new_story = Story(title=title, content=content, picture=file_path if picture else None, category= category)
    db.add(new_story)
    db.commit()

    return {"status": "success", "story_id": new_story.story_id}



async def get_story(uid: str, story_id: str, db: Session ):
    recording = db.query(Story).filter(
        Story.uid == uid,
        Story.story_id == story_id
    ).first()
    print(recording.uid)
    
    if not recording:
        raise HTTPException(status_code=404, detail="Story not found")
    if not recording.file_audio:
        raise HTTPException(status_code=405, detail="Audio story not complete")

    
    file_path =  recording.file_audio
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, media_type="audio/wav")

async def get_status_story(uid: str, story_id: str, db: Session ):
    recording = db.query(Story).filter(
        Story.uid == uid,
        Story.story_id == story_id
    ).first()
    print(recording)

    if not recording:
        raise HTTPException(status_code=404, detail="Story not found")

    
    return JSONResponse(status_code=200,content={
        "status":recording.status
    })



async def delete_story(story_id: str, db: Session = Depends(get_db)):
    # Tìm câu chuyện
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Tìm và xóa tất cả bản ghi âm liên quan
    recordings = db.query(VoiceRecording).filter(VoiceRecording.story_id == story_id).all()
    
    for recording in recordings:
        # Xóa file âm thanh
        file_path = os.path.join(VOICE_DIR, recording.file_path)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not delete file {file_path}: {str(e)}")
        
        # Xóa bản ghi âm từ database
        db.delete(recording)
    
    # Xóa câu chuyện từ database
    db.delete(story)
    db.commit()
    
    return {"status": "success", "detail": "Story and all related recordings deleted"}






async def get_story_recordings(story_id: str, db: Session = Depends(get_db)):
    # Tìm câu chuyện
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Tìm tất cả bản ghi âm của câu chuyện này - lấy tất cả, không lọc theo processed
    recordings = db.query(VoiceRecording).filter(
        VoiceRecording.story_id == story_id
    ).order_by(VoiceRecording.created_at.desc()).all()
    
    if not recordings:
        return []  # Trả về mảng trống thay vì ném ra ngoại lệ
    
    # Lấy thông tin user và thông tin story cho mỗi bản ghi
    result = []
    for rec in recordings:
        user = db.query(User).filter(User.uid == rec.uid).first()
        user_email = user.email if user else "Unknown"
        
        result.append({
            "recording_id": rec.id,
            "story_id": rec.story_id,
            "user_id": rec.uid,
            "user_email": user_email,
            "processed": rec.processed,
            "created_at": rec.created_at.isoformat()
        })
    