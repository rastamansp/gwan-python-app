import os
from typing import Optional
from docling import Document
from openai import OpenAI
from src.models.pdf_processing import PDFProcessing
from sqlalchemy.orm import Session

class PDFProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    def process_pdf(self, pdf_file, prompt: str, filename: str) -> PDFProcessing:
        """Processa um arquivo PDF e o converte em Markdown."""
        # Cria registro no banco de dados
        processing = PDFProcessing(
            original_filename=filename,
            prompt=prompt,
            status="processing"
        )
        self.db.add(processing)
        self.db.commit()

        try:
            # Extrai texto do PDF
            text = self.extract_text_from_pdf(pdf_file)
            
            # Converte para Markdown
            markdown_content = self.convert_to_markdown(text, prompt)
            
            # Atualiza o registro
            processing.markdown_content = markdown_content
            processing.status = "completed"
            self.db.commit()
            
            return processing
        except Exception as e:
            # Em caso de erro, atualiza o status
            processing.status = "failed"
            processing.error_message = str(e)
            self.db.commit()
            raise 