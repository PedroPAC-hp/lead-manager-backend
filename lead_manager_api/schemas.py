# lead_manager_api/schemas.py

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

# --- Modelos de Usuário ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserPublic(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    role: str
    created_at: datetime
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

# --- Modelos de Token ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Modelos de Configuração de Produto ---
class ResponsavelConfig(BaseModel):
    id: int
    nome: str
    inicio: int
    fim: int

class ProductConfigCreate(BaseModel):
    product_name: str
    webhook_url: str
    company_title: str
    source_id: str
    responsaveis: List[ResponsavelConfig]

class ProductConfigPublic(ProductConfigCreate):
    id: str = Field(alias="_id")
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
