from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from utils.database import Base

class VoicePrint(Base):
    __tablename__ = "voice_print"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Unique ID for each voice print record

    uid = Column(String(36), ForeignKey('users.uid'), nullable=False)  # Reference to the user
    story_id = Column(Integer, ForeignKey('stories.story_id'), nullable=False)  # Reference to the story

    status = Column(Enum('finish', 'process', 'denial', name='status_enum'), nullable=False, default="denial")
    file_audio = Column(String(255), nullable=True)
    


    # Relationships
    user = relationship("User", back_populates="voice_prints")
    story = relationship("Story", back_populates="voice_prints")
