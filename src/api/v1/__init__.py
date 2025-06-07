"""
API v1 do Gwan Python App.
"""
from fastapi import APIRouter
from src.api.v1.endpoints import users, convert

router = APIRouter(prefix="/v1")

# Registra os routers dos endpoints
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(convert.router, prefix="/convert", tags=["convert"]) 