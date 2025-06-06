from bson import ObjectId
import json
import os

class ProcessKnowledgeMessage:
    def __init__(self, mongo_service, minio_service, logger):
        self.mongo = mongo_service
        self.minio = minio_service
        self.logger = logger

    def execute(self, ch, method, properties, body):
        try:
            self.logger.info("\n==================== INÍCIO DO PROCESSAMENTO DA MENSAGEM ====================")
            self.logger.info("Mensagem recebida do RabbitMQ!")
            self.logger.info(f"Conteúdo bruto: {body}")
            message = json.loads(body.decode())
            self.logger.info(f"Mensagem decodificada: {json.dumps(message, indent=2)}")

            # 1. Validação dos campos obrigatórios
            self.logger.info("-- Validação dos campos obrigatórios --")
            knowledge_base_id = message.get('knowledgeBaseId')
            user_id = message.get('userId')
            bucket_file_id = message.get('bucketFileId')
            if not knowledge_base_id or not user_id or not bucket_file_id:
                self.logger.error("[ERRO] Campos obrigatórios knowledgeBaseId, userId e bucketFileId não informados!")
                self.logger.info("==================== FIM DO PROCESSAMENTO DA MENSAGEM ====================\n")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            self.logger.info(f"knowledgeBaseId: {knowledge_base_id}")
            self.logger.info(f"userId: {user_id}")
            self.logger.info(f"bucketFileId: {bucket_file_id}")

            # 2. Buscar knowledge base
            self.logger.info("-- Buscando KnowledgeBase no MongoDB --")
            kb = self.mongo.db.knowledgebases.find_one({'_id': ObjectId(knowledge_base_id)})
            if kb:
                self.logger.info(f"KnowledgeBase encontrada: {json.dumps(kb, default=str, indent=2)}")
            else:
                self.logger.warning(f"[AVISO] KnowledgeBase não encontrada para o id: {knowledge_base_id}")

            # 3. Buscar usuário
            self.logger.info("-- Buscando Usuário no MongoDB --")
            user = self.mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user:
                self.logger.info(f"Usuário encontrado: {json.dumps(user, default=str, indent=2)}")
            else:
                self.logger.warning(f"[AVISO] Usuário não encontrado para o id: {user_id}")

            # 4. Buscar arquivo pelo bucketFileId
            self.logger.info("-- Buscando Arquivo no MongoDB --")
            file_doc = self.mongo.db.bucketfiles.find_one({'_id': ObjectId(bucket_file_id)})
            if not file_doc:
                self.logger.error(f"[ERRO] Arquivo com bucketFileId '{bucket_file_id}' não encontrado")
                self.logger.info("==================== FIM DO PROCESSAMENTO DA MENSAGEM ====================\n")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            self.logger.info(f"Arquivo encontrado: {json.dumps(file_doc, default=str, indent=2)}")

            # 5. Baixar arquivo do MinIO para a pasta tmp
            self.logger.info("-- Baixando arquivo do MinIO --")
            bucket = file_doc.get('bucketName', 'datasets')  # Usando bucketName do documento
            filename = file_doc.get('fileName')  # Usando fileName do documento
            if not filename:
                self.logger.error("[ERRO] Campo fileName não encontrado no documento do arquivo")
                self.logger.info("==================== FIM DO PROCESSAMENTO DA MENSAGEM ====================\n")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            minio_tmp_folder = os.getenv('MINIO_TMP_FOLDER', 'tmp')
            os.makedirs(minio_tmp_folder, exist_ok=True)
            local_path = os.path.join(minio_tmp_folder, filename)
            self.logger.info(f"Bucket: {bucket}")
            self.logger.info(f"Object Name: {filename}")
            self.logger.info(f"Destino local: {local_path}")
            try:
                self.minio.client.fget_object(bucket, filename, local_path)
                self.logger.info(f"[OK] Arquivo baixado com sucesso para: {local_path}")
            except Exception as e:
                self.logger.error(f"[ERRO] ao baixar arquivo do MinIO: {e}")

            self.logger.info("==================== FIM DO PROCESSAMENTO DA MENSAGEM ====================\n")
        except Exception as e:
            self.logger.error(f"[ERRO] ao processar mensagem: {e}")
            self.logger.info("==================== FIM DO PROCESSAMENTO DA MENSAGEM ====================\n")
        ch.basic_ack(delivery_tag=method.delivery_tag) 