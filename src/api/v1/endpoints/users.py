"""
Endpoints relacionados a usuários.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database.config import get_db
from src.core.domain.user import User, UserCreate
from src.core.services.user_service import UserService
from src.api.v1.dependencies.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna lista de usuários.
    
    Args:
        skip: Número de registros para pular
        limit: Limite de registros por página
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        Lista de usuários
    """
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)

@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo usuário.
    
    Args:
        user: Dados do usuário
        db: Sessão do banco de dados
        
    Returns:
        Usuário criado
    """
    user_service = UserService(db)
    return user_service.create_user(user) 