"""
Aplicação principal do Gwan Python App.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import router as api_v1_router
from src.infrastructure.logging.logger import setup_logging
from src.infrastructure.config.settings import settings

# Configura o logging
setup_logging()

# Cria a aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API da Gwan Company",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar com as origens permitidas em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os routers
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """
    Endpoint raiz da API.
    
    Returns:
        dict: Mensagem de boas-vindas
    """
    return {
        "message": "Bem-vindo à API da Gwan Company",
        "version": "0.1.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health")
async def health_check():
    """
    Endpoint de verificação de saúde da API.
    
    Returns:
        dict: Status da API
    """
    return {
        "status": "healthy",
        "version": "0.1.0"
    } 