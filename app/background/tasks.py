import os
import logging
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from celery import Celery
from utils.database import Session, SessionLocal,get_db
from models.story import Story
from models.VoicePrint import VoicePrint
from fastapi import UploadFile, HTTPException
from dotenv import load_dotenv
from models.voice import VoiceRecording

from typing import Optional
from utils.zero_shot_tts import ZeroShotTts
from models.user import User
load_dotenv()
BROKER_URL = os.getenv("BROKER_URL", "redis://localhost:6379/0")  # fallback
BACKEND_URL = os.getenv("BACKEND_URL", "redis://localhost:6379/0")
AUDIO_DIR =  "voice_files"

celery_app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL)


# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,  # Ghi log mức INFO trở lên
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Global variable to track if the model is initialized
zero_shot_tts = None
# Get the base directory of your project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Define model path relative to base dir
MODEL_PATH = os.path.join(BASE_DIR, "app", "BreezyVoice", "pretrain_models")
@celery_app.task(name="background.tasks.create_story_task")
def create_story_task(voice_print_id: str, prompt_text: str):
    """Chạy Zero-Shot TTS để tạo file âm thanh và cập nhật trạng thái story"""
    
    logging.info(f"🚀 [Task] Bắt đầu tạo audio cho VoicePrint ID: {voice_print_id}")

    global zero_shot_tts

    # Initialize the model only if it hasn't been initialized yet
    if zero_shot_tts is None:
        model_path = MODEL_PATH
        zero_shot_tts = ZeroShotTts(model_path=model_path)
        logging.info("✅ ZeroShotTts model initialized")

    # Create database session
    db = SessionLocal()
    
    try:
        voice_print = db.query(VoicePrint).filter(VoicePrint.id == voice_print_id).first()
        if not voice_print:
            logging.error(f"❌ VoicePrint with ID {voice_print_id} not found")
            raise HTTPException(status_code=404, detail="VoicePrint not found")

        story = db.query(Story).filter(Story.story_id == voice_print.story_id).first()
        if not story:
            logging.error(f"❌ Story with ID {voice_print.story_id} not found")
            raise HTTPException(status_code=404, detail="Story not found")

        recording = db.query(VoiceRecording).filter(VoiceRecording.uid == voice_print.uid).first()
        if not recording or not recording.file_path:
            logging.error("❌ User has no valid voice recording!")
            raise HTTPException(status_code=405, detail="User does not have a valid voice recording")

        content = story.content
        user_audio_dir = os.path.join(AUDIO_DIR, voice_print.uid)
        os.makedirs(user_audio_dir, exist_ok=True)  # Ensure output directory exists

        speaker_prompt_audio_path = os.path.join(AUDIO_DIR, recording.file_path)
        output_audio_filename = f"{story.story_id}.wav"
        output_audio_path = os.path.join(user_audio_dir, output_audio_filename)

        # Run Zero-Shot TTS synthesis
        zero_shot_tts.synthesize(speaker_prompt_audio_path, output_audio_path, content, prompt_text)
        
        voice_print.file_audio = output_audio_path
        voice_print.status = "finish"
        db.commit()

        logging.info(f"✅ [Task] TTS tạo file âm thanh thành công: {output_audio_path}")
    
    except Exception as e:
        logging.error(f"❌ [Task] Lỗi khi tạo file âm thanh: {str(e)}")

    finally:
        db.close()