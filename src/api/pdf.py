from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from src.database.config import get_db
from src.core.pdf_processor import PDFProcessor
from src.models.pdf_processing import PDFProcessing
from src.models.user import User

router = APIRouter(prefix="/pdf", tags=["pdf"])

class PDFProcessingResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    prompt: str
    markdown_content: Optional[str]
    minio_path: Optional[str]
    status: str
    error_message: Optional[str]

    class Config:
        orm_mode = True

@router.post("/convert", response_model=PDFProcessingResponse)
async def convert_pdf_to_markdown(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Converte um arquivo PDF em Markdown usando a OpenAI.
    
    - **file**: Arquivo PDF a ser convertido
    - **prompt**: Instruções para a conversão em Markdown
    - **user_id**: ID do usuário que está fazendo a conversão
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF")

    # Verifica se o usuário existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    try:
        processor = PDFProcessor(db)
        result = processor.process_pdf(file.file, prompt, file.filename, user_id)
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

@router.get("/user/{user_id}", response_model=list[PDFProcessingResponse])
def get_user_processings(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém todos os processamentos de PDF de um usuário.
    
    - **user_id**: ID do usuário
    """
    # Verifica se o usuário existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    processings = db.query(PDFProcessing).filter(PDFProcessing.user_id == user_id).all()
    return processings 