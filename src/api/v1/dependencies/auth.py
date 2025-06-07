"""
Dependências de autenticação para a API.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.database.config import get_db
from src.core.domain.user import User
from src.core.services.user_service import UserService
from src.infrastructure.config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtém o usuário atual baseado no token JWT.
    
    Args:
        token: Token JWT
        db: Sessão do banco de dados
        
    Returns:
        Usuário autenticado
        
    Raises:
        HTTPException: Se o token for inválido ou o usuário não existir
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
        
    return user 