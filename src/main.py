from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.users import router as users_router

app = FastAPI(
    title="Gwan Python App",
    description="API da Gwan Company",
    version="0.1.0"
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
app.include_router(users_router)

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API da Gwan Company"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0"
    } 