# lead_manager_api/api/config_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated

from ..database import get_database
from ..security import get_current_active_user
from ..schemas import ProductConfigCreate, ProductConfigPublic, UserPublic
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

# Função helper para garantir que apenas administradores acessem
async def get_admin_user(current_user: Annotated[UserPublic, Depends(get_current_active_user)]):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado: somente administradores podem realizar esta ação."
        )
    return current_user

@router.post("/", response_model=ProductConfigPublic, status_code=status.HTTP_201_CREATED)
async def create_product_config(
    config_data: ProductConfigCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    # A linha abaixo garante que esta rota só pode ser usada por um admin
    admin_user: UserPublic = Depends(get_admin_user)
):
    """
    Cria uma nova configuração de produto.
    Acessível somente por usuários com a role 'admin'.
    """
    config_dict = config_data.model_dump(by_alias=True)
    
    # Verifica se um produto com o mesmo nome já existe
    existing_config = await db["products"].find_one({"nome": config_dict["nome"]})
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma configuração para o produto '{config_dict['nome']}'."
        )
        
    result = await db["products"].insert_one(config_dict)
    new_config = await db["products"].find_one({"_id": result.inserted_id})
    return new_config

@router.get("/", response_model=List[ProductConfigPublic])
async def list_product_configs(
    db: AsyncIOMotorDatabase = Depends(get_database),
    # Qualquer usuário logado pode ver as configurações
    current_user: UserPublic = Depends(get_current_active_user)
):
    """
    Lista todas as configurações de produto existentes.
    Acessível por qualquer usuário logado.
    """
    configs = await db["products"].find().to_list(length=100)
    return configs
