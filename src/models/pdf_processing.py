from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database.config import Base

class PDFProcessing(Base):
    __tablename__ = "pdf_processing"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_filename = Column(String)
    prompt = Column(Text)
    markdown_content = Column(Text)
    minio_path = Column(String, nullable=True)  # Caminho do arquivo no MinIO
    status = Column(String)  # 'pending', 'processing', 'completed', 'failed'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento com o usuário
    user = relationship("User", back_populates="pdf_processings") 