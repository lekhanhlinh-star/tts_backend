import os
import logging
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from celery import Celery
from utils.database import Session, SessionLocal,get_db
from models.story import Story
from fastapi import UploadFile, HTTPException
from dotenv import load_dotenv

from typing import Optional
from utils.zero_shot_tts import ZeroShotTts
from models.user import User
load_dotenv()
BROKER_URL = os.getenv("BROKER_URL", "redis://localhost:6379/0")  # fallback
BACKEND_URL = os.getenv("BACKEND_URL", "redis://localhost:6379/0")

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
def create_story_task(story_id: str, speaker_prompt_audio_path: str, output_audio_path: str, content: str):
    """Chạy Zero-Shot TTS để tạo file âm thanh và cập nhật trạng thái story"""
    
    logging.info(f"🚀 [Task] Bắt đầu tạo audio cho Story ID: {story_id}")

    global zero_shot_tts

    # Initialize the model only if it hasn't been initialized yet
    if zero_shot_tts is None:
        model_path = MODEL_PATH
        zero_shot_tts = ZeroShotTts(model_path=model_path)
        logging.info(f"✅ ZeroShotTts model initialized")

    # Create database session
    db = SessionLocal()
    
    try:
        if zero_shot_tts is None:
            logging.error("❌ ZeroShotTts model is not initialized!")
            raise Exception("ZeroShotTts model not initialized")

        # Run Zero-Shot TTS synthesis
        zero_shot_tts.synthesize(speaker_prompt_audio_path, output_audio_path, content)
        logging.info(f"✅ [Task] TTS tạo file âm thanh thành công: {output_audio_path}")
        
        # Update story status to "completed"
        story = db.query(Story).filter(Story.story_id == story_id).first()
        if story:
            story.status = "finish"
            story.file_audio = output_audio_path
            db.commit()
            logging.info(f"✅ [Task] Story ID {story_id} đã được cập nhật thành 'completed'")
        else:
            logging.warning(f"⚠️ [Task] Không tìm thấy Story ID {story_id} để cập nhật!")

    except Exception as e:
        logging.error(f"❌ [Task] Lỗi khi tạo file âm thanh cho Story ID {story_id}: {str(e)}")
        
    
    finally:
        db.close()  # Ensure the session is closed to prevent resource leaks
