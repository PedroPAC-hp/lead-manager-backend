# lead_manager_api/schemas.py

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic.functional_validators import BeforeValidator
from typing import Optional, List, Annotated
from datetime import datetime

# Representa um ObjectId da BSON, mas permite que seja validado a partir de uma string.
# BeforeValidator aplica a função `str` a qualquer input, garantindo que o Pydantic o trate como string.
PyObjectId = Annotated[str, BeforeValidator(str)]

# --- Modelos de Usuário ---
class UserPublic(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: EmailStr
    role: str
    created_at: datetime
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"example": {
            "id": "60d5f3f77c3b4a001f3e8c6c",
            "email": "user@example.com",
            "role": "member",
            "created_at": "2025-11-14T20:00:00Z"
        }},
    )

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

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

class ProductConfigPublic(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    product_name: str
    webhook_url: str
    company_title: str
    source_id: str
    responsaveis: List[ResponsavelConfig]
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class ProductConfigCreate(BaseModel):
    product_name: str
    webhook_url: str
    company_title: str
    source_id: str
    responsaveis: List[ResponsavelConfig]

# --- Modelos de Lead (para o futuro) ---
class LeadPublic(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    # Adicionaremos outros campos aqui
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class LeadUpdate(BaseModel):
    # Campos que podem ser atualizados
    pass
