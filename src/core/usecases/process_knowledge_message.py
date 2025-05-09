class ProcessKnowledgeMessage:
    def __init__(self, mongo_service, minio_service, logger):
        self.mongo = mongo_service
        self.minio = minio_service
        self.logger = logger

    def execute(self, ch, method, properties, body):
        try:
            import json
            import os
            self.logger.info("\n==================== INÍCIO DO PROCESSAMENTO DA MENSAGEM ====================")
            self.logger.info("Mensagem recebida do RabbitMQ!")
            self.logger.info(f"Conteúdo bruto: {body}")
            message = json.loads(body.decode())
            self.logger.info(f"Mensagem decodificada: {json.dumps(message, indent=2)}")

            # 1. Validação dos campos obrigatórios
            self.logger.info("-- Validação dos campos obrigatórios --")
            knowledge_base_id = message.get('knowledgeBaseId')
            user_id = message.get('userId')
            filename = message.get('filename')
            if not knowledge_base_id or not user_id or not filename:
                self.logger.error("[ERRO] Campos obrigatórios knowledgeBaseId, userId e filename não informados!")
                self.logger.info("==================== FIM DO PROCESSAMENTO DA MENSAGEM ====================\n")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            self.logger.info(f"knowledgeBaseId: {knowledge_base_id}")
            self.logger.info(f"userId: {user_id}")
            self.logger.info(f"filename: {filename}")

            # 2. Buscar knowledge base
            self.logger.info("-- Buscando KnowledgeBase no MongoDB --")
            kb = self.mongo.db.knowledgebases.find_one({'_id': knowledge_base_id})
            if kb:
                self.logger.info(f"KnowledgeBase encontrada: {json.dumps(kb, default=str, indent=2)}")
            else:
                self.logger.warning(f"[AVISO] KnowledgeBase não encontrada para o id: {knowledge_base_id}")

            # 3. Buscar usuário
            self.logger.info("-- Buscando Usuário no MongoDB --")
            user = self.mongo.db.users.find_one({'_id': user_id})
            if user:
                self.logger.info(f"Usuário encontrado: {json.dumps(user, default=str, indent=2)}")
            else:
                self.logger.warning(f"[AVISO] Usuário não encontrado para o id: {user_id}")

            # 4. Buscar arquivo correto do usuário
            self.logger.info("-- Buscando Arquivo no MongoDB --")
            file_doc = self.mongo.db.bucketfiles.find_one({'userId': user_id, 'filename': filename})
            if not file_doc:
                self.logger.error(f"[ERRO] Arquivo '{filename}' não encontrado para o usuário {user_id}")
                self.logger.info("==================== FIM DO PROCESSAMENTO DA MENSAGEM ====================\n")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            self.logger.info(f"Arquivo encontrado: {json.dumps(file_doc, default=str, indent=2)}")

            # 5. Baixar arquivo do MinIO para a pasta tmp
            self.logger.info("-- Baixando arquivo do MinIO --")
            bucket = file_doc.get('bucket', 'datasets')
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