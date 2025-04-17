# models/user.py
from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime, String
from utils.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    uid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    voice_prints = relationship("VoicePrint", back_populates="user")
