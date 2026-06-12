import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_histories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    execution_code = Column(Text, nullable=True)
    response_text = Column(Text, nullable=False)
    visualization_config = Column(JSON, nullable=True) # Definition for UI runtime rendering
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="chat_histories")
