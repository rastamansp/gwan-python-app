from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from src.database.config import Base

class PDFProcessing(Base):
    __tablename__ = "pdf_processing"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String)
    prompt = Column(Text)
    markdown_content = Column(Text)
    status = Column(String)  # 'pending', 'processing', 'completed', 'failed'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 