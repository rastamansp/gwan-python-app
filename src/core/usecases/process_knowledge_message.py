from bson import ObjectId
import json
import os
from pathlib import Path
from docling.document_converter import DocumentConverter
from datetime import datetime
import logging
from typing import Dict, Any
from src.core.repositories.knowledge_base_repository import KnowledgeBaseRepository
from src.core.repositories.bucket_file_repository import BucketFileRepository
from src.core.repositories.user_repository import UserRepository
from src.core.services.document_processor_service import DocumentProcessorService

class ProcessKnowledgeMessage:
    def __init__(self, mongo_service, minio_service, logger, vector_db_service):
        self.mongo = mongo_service
        self.minio = minio_service
        self.logger = logger
        self.converter = DocumentConverter()
        self.vector_db = vector_db_service
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

        self.kb_repository = KnowledgeBaseRepository(mongo_service)
        self.file_repository = BucketFileRepository(mongo_service)
        self.user_repository = UserRepository(mongo_service)
        self.doc_processor = DocumentProcessorService(minio_service, logger)

    def execute(self, ch, method, properties, body):
        try:
            self.logger.info("\n==================== INÍCIO DO PROCESSAMENTO ====================")
            message = json.loads(body.decode())
            self.logger.info(f"Requisição: {json.dumps(message, indent=2)}")

            # 1. Validação dos campos obrigatórios
            knowledge_base_id = message.get('knowledgeBaseId')
            user_id = message.get('userId')
            bucket_file_id = message.get('bucketFileId')
            if not self._validate_required_fields(knowledge_base_id, user_id, bucket_file_id):
                self._ack_message(ch, method)
                return

            # 2. Buscar e validar dados
            kb, user, file_doc = self._fetch_and_validate_data(knowledge_base_id, user_id, bucket_file_id)
            if not all([kb, user, file_doc]):
                self._ack_message(ch, method)
                return

            # 3. Processar o documento
            try:
                # Baixar e processar o arquivo
                bucket = file_doc.get('bucketName', 'datasets')
                filename = file_doc.get('fileName')
                original_name = file_doc.get('originalName', filename)
                
                markdown_path, markdown_content = self.doc_processor.download_and_process_file(
                    bucket, filename, original_name
                )

                # Preparar metadados
                metadata = self.doc_processor.prepare_metadata(
                    user_id=str(user_id),
                    user_name=user.get('name', ''),
                    user_email=user.get('email', ''),
                    file_name=original_name,
                    file_id=str(bucket_file_id),
                    knowledge_base_id=str(knowledge_base_id),
                    knowledge_base_name=kb.get('name', ''),
                    markdown_path=markdown_path,
                    bucket_name=bucket,
                    original_file_name=filename
                )

                # Processar embeddings
                chunks = self.doc_processor.split_content(markdown_content)
                self.vector_db.store_embeddings_batch(chunks, metadata)
                self.logger.info(f"[OK] Processamento concluído: {len(chunks)} chunks processados")

                # Atualizar status
                self.file_repository.update_processing_status(
                    bucket_file_id,
                    status='completed',
                    markdown_path=markdown_path,
                    total_chunks=len(chunks)
                )
                self.kb_repository.update_after_processing(knowledge_base_id, bucket_file_id)

            except Exception as e:
                self.logger.error(f"[ERRO] Falha no processamento: {e}")
                self._handle_processing_error(knowledge_base_id, bucket_file_id, str(e))

            self.logger.info("==================== FIM DO PROCESSAMENTO ====================\n")
            
        except Exception as e:
            self.logger.error(f"[ERRO] Falha geral: {e}")
            self.logger.info("==================== FIM DO PROCESSAMENTO ====================\n")
            
        self._ack_message(ch, method)

    def _validate_required_fields(self, knowledge_base_id: str, user_id: str, bucket_file_id: str) -> bool:
        """Valida os campos obrigatórios da mensagem."""
        if not knowledge_base_id or not user_id or not bucket_file_id:
            self.logger.error("[ERRO] Campos obrigatórios não informados")
            return False
        return True

    def _fetch_and_validate_data(self, knowledge_base_id: str, user_id: str, bucket_file_id: str) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """Busca e valida os dados necessários para o processamento."""
        kb = self.kb_repository.find_by_id(knowledge_base_id)
        if not kb:
            self.logger.error(f"[ERRO] KnowledgeBase não encontrada: {knowledge_base_id}")
            return None, None, None

        user = self.user_repository.find_by_id(user_id)
        if not user:
            self.logger.error(f"[ERRO] Usuário não encontrado: {user_id}")
            return None, None, None

        file_doc = self.file_repository.find_by_id(bucket_file_id)
        if not file_doc:
            self.logger.error(f"[ERRO] Arquivo não encontrado: {bucket_file_id}")
            return None, None, None

        if not file_doc.get('fileName'):
            self.logger.error("[ERRO] Campo fileName não encontrado")
            return None, None, None

        return kb, user, file_doc

    def _handle_processing_error(self, knowledge_base_id: str, bucket_file_id: str, error: str) -> None:
        """Atualiza o status em caso de erro no processamento."""
        self.file_repository.update_processing_status(
            bucket_file_id,
            status='failed',
            error=error
        )
        self.kb_repository.update_status(
            knowledge_base_id,
            status='error',
            error=error
        )

    def _ack_message(self, ch, method) -> None:
        """Confirma o processamento da mensagem."""
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _split_content(self, content: str, max_chunk_size: int = 1000) -> list:
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