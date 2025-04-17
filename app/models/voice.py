
from datetime import datetime
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String,Text
from utils.database import Base


class VoiceRecording(Base):
    __tablename__ = "voice_recordings"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    uid = Column(String(36), ForeignKey("users.uid", ondelete="CASCADE"), index=True, nullable=False)
    prompt_text = Column(Text, nullable=False)
    file_path = Column(String(255), nullable=False)
    processed = Column(Boolean, default=False)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
