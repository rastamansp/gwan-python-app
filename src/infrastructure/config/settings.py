"""
Configurações centralizadas da aplicação.
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Configurações do Banco de Dados
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # Configurações do RabbitMQ
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    
    # Configurações do MongoDB
    MONGODB_URI: str
    MONGODB_DB: str
    
    # Configurações do MinIO
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool = True
    MINIO_TMP_FOLDER: str = "tmp"
    
    # Configurações da API
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "Gwan Python App"
    DEBUG: bool = False
    
    # Configurações de Segurança
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configurações do OpenAI
    OPENAI_API_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna as configurações da aplicação.
    
    Returns:
        Settings: Configurações da aplicação
        
    Note:
        Usa lru_cache para evitar recarregar as configurações
        a cada requisição
    """
    return Settings()

# Instância global das configurações
settings = get_settings() 