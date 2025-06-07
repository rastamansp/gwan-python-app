"""
Configuração centralizada de logging.
"""
import logging
import sys
import structlog
from typing import Any, Dict

from src.infrastructure.config.settings import settings

def setup_logging() -> None:
    """
    Configura o logging da aplicação.
    
    Configura:
    - Formato JSON para logs
    - Timestamp ISO
    - Níveis de log baseados no ambiente
    - Processadores structlog
    """
    # Configura o nível de log baseado no ambiente
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Configura o structlog
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configura o logging padrão do Python
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Configura níveis de log específicos para bibliotecas
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.DEBUG else logging.WARNING
    )
    
    # Configura logs do RabbitMQ para mostrar apenas conexão bem-sucedida
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("pika.adapters.utils.connection_workflow").setLevel(logging.INFO)
    
    # Filtro personalizado para logs do RabbitMQ
    class RabbitMQFilter(logging.Filter):
        def filter(self, record):
            # Permite apenas logs de conexão bem-sucedida
            if record.levelno == logging.INFO and "AMQPConnector - reporting success" in record.getMessage():
                return True
            # Permite logs de erro
            if record.levelno >= logging.WARNING:
                return True
            return False
    
    # Aplica o filtro aos loggers do RabbitMQ
    rabbitmq_logger = logging.getLogger("pika")
    rabbitmq_logger.addFilter(RabbitMQFilter())
    rabbitmq_logger = logging.getLogger("pika.adapters.utils.connection_workflow")
    rabbitmq_logger.addFilter(RabbitMQFilter())

def get_logger(name: str) -> structlog.BoundLogger:
    """
    Retorna um logger configurado.
    
    Args:
        name: Nome do logger
        
    Returns:
        structlog.BoundLogger: Logger configurado
    """
    return structlog.get_logger(name)

# Exemplo de uso:
# logger = get_logger(__name__)
# logger.info("evento", 
#     user_id=user_id,
#     action="login",
#     status="success"
# ) 