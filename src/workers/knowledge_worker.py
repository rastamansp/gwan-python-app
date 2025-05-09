from infrastructure.config import get_env
from infrastructure.logger import get_logger
from core.services.mongo_service import MongoService
from core.services.minio_service import MinioService
from core.services.rabbitmq_service import RabbitMQService
from core.usecases.process_knowledge_message import ProcessKnowledgeMessage


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

    # Inicializa o caso de uso principal
    usecase = ProcessKnowledgeMessage(mongo, minio, logger)

    # Consome mensagens do RabbitMQ e processa cada uma com o usecase
    logger.info("Iniciando o worker e aguardando mensagens da fila...")
    rabbit.consume(usecase.execute)


if __name__ == '__main__':
    main()