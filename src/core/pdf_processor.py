import os
from typing import Optional
from docling import Document
from openai import OpenAI
from minio import Minio
from src.models.pdf_processing import PDFProcessing
from sqlalchemy.orm import Session
from src.core.queue_service import QueueService

class PDFProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.queue_service = QueueService()
        
        # Configuração do MinIO
        self.minio_client = Minio(
            "minio:9000",
            access_key="PJixupaJSmVKkPt0wfbw",
            secret_key="Guf303IHKS1zR1eTXiLS93SrgOj1NYtI1JbUew7u",
            secure=False
        )
        
        # Garante que o bucket existe
        if not self.minio_client.bucket_exists("pdfs"):
            self.minio_client.make_bucket("pdfs")

    def upload_to_minio(self, file_data: bytes, filename: str) -> str:
        """Faz upload do arquivo para o MinIO."""
        try:
            # Gera um nome único para o arquivo
            object_name = f"pdfs/{filename}"
            
            # Faz o upload
            self.minio_client.put_object(
                bucket_name="pdfs",
                object_name=object_name,
                data=file_data,
                length=len(file_data),
                content_type="application/pdf"
            )
            
            return object_name
        except Exception as e:
            raise Exception(f"Erro ao fazer upload para o MinIO: {str(e)}")

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extrai texto de um arquivo PDF usando Docling."""
        try:
            # Cria um documento Docling
            doc = Document(pdf_file)
            
            # Extrai o texto com formatação preservada
            text = doc.extract_text(
                preserve_formatting=True,
                preserve_tables=True,
                preserve_images=False
            )
            
            return text
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")

    def convert_to_markdown(self, text: str, prompt: str) -> str:
        """Converte texto em Markdown usando a OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Você é um especialista em converter texto em Markdown formatado, mantendo a estrutura e formatação do documento original."},
                    {"role": "user", "content": f"{prompt}\n\nTexto a ser convertido:\n{text}"}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Erro ao converter para Markdown: {str(e)}")

    def process_pdf(self, pdf_file, prompt: str, filename: str, user_id: int) -> PDFProcessing:
        """Processa um arquivo PDF e o converte em Markdown."""
        # Cria registro no banco de dados
        processing = PDFProcessing(
            user_id=user_id,
            original_filename=filename,
            prompt=prompt,
            status="pending"
        )
        self.db.add(processing)
        self.db.commit()

        try:
            # Lê o conteúdo do arquivo
            file_content = pdf_file.read()
            
            # Envia para a fila
            message = {
                "processing_id": processing.id,
                "file_data": file_content,
                "prompt": prompt,
                "filename": filename,
                "user_id": user_id
            }
            self.queue_service.publish_message(message)
            
            # Atualiza o status
            processing.status = "queued"
            self.db.commit()
            
            return processing
        except Exception as e:
            # Em caso de erro, atualiza o status
            processing.status = "failed"
            processing.error_message = str(e)
            self.db.commit()
            raise 