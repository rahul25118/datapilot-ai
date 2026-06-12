import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    storage_path = Column(String(1024), nullable=False) # Local or S3 path
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    schema_metadata = Column(JSON, nullable=True) # Column mappings and detected datatypes
    profiling_summary = Column(JSON, nullable=True) # Data health insights
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="datasets")
    chat_histories = relationship("ChatHistory", back_populates="dataset")
