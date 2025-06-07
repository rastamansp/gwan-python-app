from bson import ObjectId
import json
import os
from pathlib import Path
from docling.document_converter import DocumentConverter
from datetime import datetime
import logging

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

    def execute(self, ch, method, properties, body):
        try:
            self.logger.info("\n==================== INÍCIO DO PROCESSAMENTO ====================")
            message = json.loads(body.decode())
            self.logger.info(f"Requisição: {json.dumps(message, indent=2)}")

            # 1. Validação dos campos obrigatórios
            knowledge_base_id = message.get('knowledgeBaseId')
            user_id = message.get('userId')
            bucket_file_id = message.get('bucketFileId')
            if not knowledge_base_id or not user_id or not bucket_file_id:
                self.logger.error("[ERRO] Campos obrigatórios não informados")
                self.logger.info("==================== FIM DO PROCESSAMENTO ====================\n")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # 2. Buscar knowledge base
            kb = self.mongo.db.knowledgebases.find_one({'_id': ObjectId(knowledge_base_id)})
            if not kb:
                self.logger.error(f"[ERRO] KnowledgeBase não encontrada: {knowledge_base_id}")
                self.logger.info("==================== FIM DO PROCESSAMENTO ====================\n")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # 3. Buscar usuário no MongoDB
            mongo_user = self.mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if not mongo_user:
                self.logger.error(f"[ERRO] Usuário não encontrado: {user_id}")
                self.logger.info("==================== FIM DO PROCESSAMENTO ====================\n")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # 4. Buscar arquivo pelo bucketFileId
            file_doc = self.mongo.db.bucketfiles.find_one({'_id': ObjectId(bucket_file_id)})
            if not file_doc:
                self.logger.error(f"[ERRO] Arquivo não encontrado: {bucket_file_id}")
                self.logger.info("==================== FIM DO PROCESSAMENTO ====================\n")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # 5. Baixar arquivo do MinIO para a pasta tmp
            bucket = file_doc.get('bucketName', 'datasets')
            filename = file_doc.get('fileName')
            original_name = file_doc.get('originalName', filename)
            if not filename:
                self.logger.error("[ERRO] Campo fileName não encontrado")
                self.logger.info("==================== FIM DO PROCESSAMENTO ====================\n")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            minio_tmp_folder = os.getenv('MINIO_TMP_FOLDER', 'tmp')
            os.makedirs(minio_tmp_folder, exist_ok=True)
            local_path = os.path.join(minio_tmp_folder, filename)
            
            try:
                self.minio.client.fget_object(bucket, filename, local_path)
            except Exception as e:
                self.logger.error(f"[ERRO] Falha ao baixar arquivo: {e}")
                self.logger.info("==================== FIM DO PROCESSAMENTO ====================\n")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # 6. Processar o PDF e converter para markdown
            try:
                # Converte PDF para markdown
                result = self.converter.convert(str(local_path))
                markdown_content = result.document.export_to_markdown()

                # Salva o markdown na pasta de processados
                markdown_filename = f"{Path(original_name).stem}.md"
                markdown_path = self.processed_dir / markdown_filename
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)

                # 7. Armazenar embeddings no PostgreSQL
                metadata = {
                    "userId": str(user_id),
                    "userName": mongo_user.get('name', ''),
                    "userEmail": mongo_user.get('email', ''),
                    "fileName": original_name,
                    "fileId": str(bucket_file_id),
                    "knowledgeBaseId": str(knowledge_base_id),
                    "knowledgeBaseName": kb.get('name', '') if kb else '',
                    "markdownPath": str(markdown_path),
                    "processedAt": datetime.utcnow().isoformat(),
                    "bucketName": bucket,
                    "originalFileName": filename
                }

                # Divide o conteúdo em chunks menores para processamento
                chunks = self._split_content(markdown_content)
                self.vector_db.store_embeddings_batch(chunks, metadata)
                self.logger.info(f"[OK] Processamento concluído: {len(chunks)} chunks processados")

                # Atualiza o status do arquivo no MongoDB
                self.mongo.db.bucketfiles.update_one(
                    {'_id': ObjectId(bucket_file_id)},
                    {
                        '$set': {
                            'status': 'completed',
                            'markdownPath': str(markdown_path),
                            'updatedAt': datetime.utcnow(),
                            'embeddingsStored': True,
                            'totalChunks': len(chunks)
                        }
                    }
                )

                # Atualiza o status da knowledge base
                self.mongo.db.knowledgebases.update_one(
                    {'_id': ObjectId(knowledge_base_id)},
                    {
                        '$set': {
                            'status': 'completed',
                            'updatedAt': datetime.utcnow(),
                            'lastProcessedFile': str(bucket_file_id),
                            'lastProcessedAt': datetime.utcnow()
                        }
                    }
                )

            except Exception as e:
                self.logger.error(f"[ERRO] Falha no processamento: {e}")
                # Atualiza o status do arquivo para failed
                self.mongo.db.bucketfiles.update_one(
                    {'_id': ObjectId(bucket_file_id)},
                    {
                        '$set': {
                            'status': 'failed',
                            'error': str(e),
                            'updatedAt': datetime.utcnow()
                        }
                    }
                )

                # Atualiza o status da knowledge base para erro
                self.mongo.db.knowledgebases.update_one(
                    {'_id': ObjectId(knowledge_base_id)},
                    {
                        '$set': {
                            'status': 'error',
                            'lastError': str(e),
                            'updatedAt': datetime.utcnow()
                        }
                    }
                )
            finally:
                # Remove o arquivo temporário
                if os.path.exists(local_path):
                    os.remove(local_path)

            self.logger.info("==================== FIM DO PROCESSAMENTO ====================\n")
        except Exception as e:
            self.logger.error(f"[ERRO] Falha geral: {e}")
            self.logger.info("==================== FIM DO PROCESSAMENTO ====================\n")
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