# lead_manager_api/schemas.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

# --- Validador Customizado para ObjectId ---
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        def validate(v, validation_info):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid ObjectId")
            return ObjectId(v)
        return handler(source_type).after_validator(validate)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}

# --- Modelo Base ---
class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

# --- Modelos de Usuário ---
class UserBase(MongoBaseModel):
    email: EmailStr = Field(..., example="user@example.com")

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserPublic(UserBase):
    email: EmailStr
    role: str
    created_at: datetime

# --- Modelos de Token ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Modelos de Lead ---
class LeadBase(MongoBaseModel):
    pass # Adicionaremos campos depois

class LeadPublic(LeadBase):
    # Campos que queremos exibir publicamente
    pass

class LeadUpdate(BaseModel):
    # Campos que podem ser atualizados
    pass

# --- Modelos de Configuração de Produto (CORRIGIDO) ---

class ResponsavelConfig(BaseModel): # <-- NOVO MODELO SÓ PARA A CONFIGURAÇÃO
    id: int
    nome: str
    inicio: int
    fim: int

class ProductConfigBase(MongoBaseModel):
    product_name: str
    webhook_url: str
    company_title: str
    source_id: str
    responsaveis: List[ResponsavelConfig] # <-- USA O NOVO MODELO

class ProductConfigCreate(BaseModel): # <-- NÃO HERDA DE NADA, SÓ RECEBE DADOS
    product_name: str
    webhook_url: str
    company_title: str
    source_id: str
    responsaveis: List[ResponsavelConfig]

class ProductConfigPublic(ProductConfigBase):
    pass
