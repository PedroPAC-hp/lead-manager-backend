# lead_manager_api/api/import_routes.py

from fastapi import APIRouter, Depends
from typing import Annotated

from ..security import get_current_active_user
from ..schemas import UserPublic

router = APIRouter()

# ROTA DE TESTE SÓ PARA VER SE A AUTENTICAÇÃO FUNCIONA
@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)]
):
    return current_user
