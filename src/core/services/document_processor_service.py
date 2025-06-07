from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from docling.document_converter import DocumentConverter
import logging

class DocumentProcessorService:
    def __init__(self, minio_service, logger):
        self.minio = minio_service
        self.logger = logger
        self.converter = DocumentConverter()
        self.tmp_dir = Path("tmp")
        self.processed_dir = self.tmp_dir / "processados"
        self.tmp_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        # Configura o logger da biblioteca docling para mostrar apenas WARNING e acima
        logging.getLogger('docling').setLevel(logging.WARNING)
        logging.getLogger('docling.document_converter').setLevel(logging.WARNING)
        logging.getLogger('docling.models.factories').setLevel(logging.WARNING)
        logging.getLogger('docling.utils.accelerator_utils').setLevel(logging.WARNING)
        logging.getLogger('docling.pipeline.base_pipeline').setLevel(logging.WARNING)

    def download_and_process_file(self, bucket: str, filename: str, original_name: str) -> tuple[str, str]:
        """
        Baixa um arquivo do MinIO, processa e retorna o conteúdo em markdown.
        
        Returns:
            tuple[str, str]: (caminho do arquivo markdown, conteúdo markdown)
        """
        minio_tmp_folder = Path("tmp")
        minio_tmp_folder.mkdir(exist_ok=True)
        local_path = minio_tmp_folder / filename
        
        try:
            # Baixa o arquivo
            self.minio.client.fget_object(bucket, filename, str(local_path))
            
            # Processa o arquivo
            result = self.converter.convert(str(local_path))
            markdown_content = result.document.export_to_markdown()
            
            # Salva o markdown
            markdown_filename = f"{Path(original_name).stem}.md"
            markdown_path = self.processed_dir / markdown_filename
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                
            return str(markdown_path), markdown_content
            
        finally:
            # Remove o arquivo temporário
            if local_path.exists():
                local_path.unlink()

    def split_content(self, content: str, max_chunk_size: int = 1000) -> List[str]:
        """
        Divide o conteúdo em chunks menores para processamento.
        Tenta manter parágrafos e seções juntos.
        """
        # Divide por parágrafos
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0

        for paragraph in paragraphs:
            paragraph_size = len(paragraph)
            
            # Se o parágrafo for maior que o tamanho máximo, divide em sentenças
            if paragraph_size > max_chunk_size:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                
                sentences = paragraph.split('. ')
                current_sentence = []
                current_sentence_size = 0
                
                for sentence in sentences:
                    sentence = sentence.strip() + '. '
                    sentence_size = len(sentence)
                    
                    if current_sentence_size + sentence_size > max_chunk_size:
                        if current_sentence:
                            chunks.append(' '.join(current_sentence))
                        current_sentence = [sentence]
                        current_sentence_size = sentence_size
                    else:
                        current_sentence.append(sentence)
                        current_sentence_size += sentence_size
                
                if current_sentence:
                    chunks.append(' '.join(current_sentence))
            
            # Se adicionar o parágrafo atual exceder o tamanho máximo, finaliza o chunk atual
            elif current_size + paragraph_size > max_chunk_size:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_size = paragraph_size
            else:
                current_chunk.append(paragraph)
                current_size += paragraph_size

        # Adiciona o último chunk se houver
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    def prepare_metadata(self, user_id: str, user_name: str, user_email: str, 
                        file_name: str, file_id: str, knowledge_base_id: str, 
                        knowledge_base_name: str, markdown_path: str, 
                        bucket_name: str, original_file_name: str) -> Dict[str, Any]:
        """Prepara os metadados para o processamento do documento."""
        return {
            "userId": user_id,
            "userName": user_name,
            "userEmail": user_email,
            "fileName": file_name,
            "fileId": file_id,
            "knowledgeBaseId": knowledge_base_id,
            "knowledgeBaseName": knowledge_base_name,
            "markdownPath": markdown_path,
            "processedAt": datetime.utcnow().isoformat(),
            "bucketName": bucket_name,
            "originalFileName": original_file_name
        } 