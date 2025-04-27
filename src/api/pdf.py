from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from src.database.config import get_db
from src.core.pdf_processor import PDFProcessor
from src.models.pdf_processing import PDFProcessing

router = APIRouter(prefix="/pdf", tags=["pdf"])

class PDFProcessingResponse(BaseModel):
    id: int
    original_filename: str
    prompt: str
    markdown_content: Optional[str]
    status: str
    error_message: Optional[str]

    class Config:
        orm_mode = True

@router.post("/convert", response_model=PDFProcessingResponse)
async def convert_pdf_to_markdown(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Converte um arquivo PDF em Markdown usando a OpenAI.
    
    - **file**: Arquivo PDF a ser convertido
    - **prompt**: Instruções para a conversão em Markdown
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF")

    try:
        processor = PDFProcessor(db)
        result = processor.process_pdf(file.file, prompt, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{processing_id}", response_model=PDFProcessingResponse)
def get_processing_status(
    processing_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém o status de um processamento de PDF.
    
    - **processing_id**: ID do processamento
    """
    processing = db.query(PDFProcessing).filter(PDFProcessing.id == processing_id).first()
    if not processing:
        raise HTTPException(status_code=404, detail="Processamento não encontrado")
    return processing 