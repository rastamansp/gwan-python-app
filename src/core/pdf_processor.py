import os
import warnings
from datetime import datetime
from pathlib import Path
from docling.document_converter import DocumentConverter
from sqlalchemy.orm import Session
from src.models.pdf_processing import PDFProcessing

# Suprime avisos específicos
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")
warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.data.dataloader")

class PDFProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.converter = DocumentConverter()
        self.tmp_dir = Path("tmp")
        self.tmp_dir.mkdir(exist_ok=True)

    def process_pdf(self, file_data: bytes, prompt: str, filename: str, user_id: int) -> dict:
        """
        Processa um arquivo PDF e retorna o conteúdo em markdown.
        
        Args:
            file_data (bytes): Conteúdo do arquivo PDF
            prompt (str): Prompt para processamento
            filename (str): Nome original do arquivo
            user_id (int): ID do usuário
            
        Returns:
            dict: Resultado do processamento
        """
        try:
            # Salva o arquivo temporariamente
            tmp_file = self.tmp_dir / filename
            with open(tmp_file, "wb") as f:
                f.write(file_data)

            # Cria registro no banco
            processing = PDFProcessing(
                user_id=user_id,
                original_filename=filename,
                prompt=prompt,
                status="processing"
            )
            self.db.add(processing)
            self.db.commit()

            try:
                # Converte PDF para markdown
                result = self.converter.convert(str(tmp_file))
                markdown_content = result.document.export_to_markdown()

                # Atualiza o registro com o conteúdo
                processing.markdown_content = markdown_content
                processing.status = "completed"
                self.db.commit()

                return {
                    "status": "success",
                    "processing_id": processing.id,
                    "markdown_content": markdown_content
                }

            except Exception as e:
                # Em caso de erro, atualiza o status
                processing.status = "failed"
                processing.error_message = str(e)
                self.db.commit()
                raise

            finally:
                # Remove o arquivo temporário
                if tmp_file.exists():
                    tmp_file.unlink()

        except Exception as e:
            raise Exception(f"Erro ao processar PDF: {str(e)}") 