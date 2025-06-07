from src.infrastructure.config import get_env
from src.infrastructure.logger import get_logger
from src.core.services.mongo_service import MongoService
from src.core.services.minio_service import MinioService
from src.core.services.rabbitmq_service import RabbitMQService
from src.core.services.vector_service import VectorService
from src.core.usecases.process_knowledge_message import ProcessKnowledgeMessage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.config import Base
from src.models.document_embedding import DocumentEmbedding

class VectorDBService:
    def __init__(self, postgres_url: str):
        self.engine = create_engine(postgres_url)
        self.Session = sessionmaker(bind=self.engine)
        self.vector_service = VectorService(self.Session())
        # Cria a tabela (com os campos necessários) desde o início
        Base.metadata.create_all(bind=self.engine)

    def store_embedding(
        self,
        content: str,
        meta: dict
    ):
        """Armazena o conteúdo e seu embedding no banco de dados."""
        # Extrai os campos necessários do meta
        knowledge_base_id = meta.get('knowledgeBaseId')
        user_id = meta.get('userId')
        bucket_file_id = meta.get('fileId')
        chunk_index = meta.get('chunkIndex', 0)

        # Armazena o embedding usando o VectorService
        self.vector_service.store_embedding(
            knowledge_base_id=knowledge_base_id,
            user_id=user_id,
            bucket_file_id=bucket_file_id,
            chunk_index=chunk_index,
            content=content,
            meta=meta
        )

    def store_embeddings_batch(self, chunks: list, meta: dict, batch_size: int = 2):
        """
        Recebe uma lista de textos (chunks) e um dict meta base, e faz o batch insert conforme a interface DocumentEmbeddingInput.
        
        Args:
            chunks: Lista de textos para gerar embeddings
            meta: Dicionário com metadados base
            batch_size: Tamanho do lote para inserção (padrão: 2)
        """
        embeddings_data = []
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            chunk_meta = meta.copy()
            chunk_meta.update({
                "chunkIndex": i,
                "totalChunks": total_chunks
            })
            embeddings_data.append({
                "knowledgeBaseId": chunk_meta.get('knowledgeBaseId'),
                "userId": chunk_meta.get('userId'),
                "bucketFileId": chunk_meta.get('fileId'),
                "chunkIndex": i,
                "content": chunk,
                "meta": chunk_meta
            })
        self.vector_service.store_embeddings_batch(embeddings_data, batch_size=batch_size)

def main():
    # Inicializa logger
    logger = get_logger(__name__)

    # Inicializa serviços externos
    mongo = MongoService(get_env('MONGODB_URI'), get_env('MONGODB_DB'))
    minio = MinioService(
        get_env('MINIO_ENDPOINT'),
        get_env('MINIO_ACCESS_KEY'),
        get_env('MINIO_SECRET_KEY'),
        get_env('MINIO_SECURE', 'true').lower() == 'true'
    )
    rabbit = RabbitMQService(
        get_env('RABBITMQ_HOST'),
        int(get_env('RABBITMQ_PORT', 5672)),
        get_env('RABBITMQ_USER'),
        get_env('RABBITMQ_PASSWORD'),
        'knowledge_base_processing'
    )
    
    # Inicializa o serviço de vetores
    vector_db = VectorDBService(get_env('POSTGRES_URL'))

    # Inicializa o caso de uso principal com o serviço de vetores
    usecase = ProcessKnowledgeMessage(mongo, minio, logger, vector_db)

    # Consome mensagens do RabbitMQ e processa cada uma com o usecase
    logger.info("Iniciando o worker e aguardando mensagens da fila...")
    rabbit.consume(usecase.execute)

if __name__ == '__main__':
    main()