# models/story.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from utils.database import Base
import uuid
from datetime import datetime

class Story(Base):
    __tablename__ = "stories"
    story_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # Added content field
    category = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    picture = Column(String(255), nullable=True)  # Added image path storage
    voice_prints = relationship("VoicePrint", back_populates="story")


 
