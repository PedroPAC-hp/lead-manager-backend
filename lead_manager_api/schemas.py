# backend/lead_manager_api/schemas.py

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema

# --- Configuração para ObjectId do MongoDB ---
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, validation_info):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, source_type, handler):
        # AQUI ESTÁ A CORREÇÃO FINAL: 'StringSchema' com 'S' maiúsculo
        return core_schema.StringSchema()
    
# --- Modelos de Usuário ---
class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="uma_senha_forte_123")

class UserInDB(UserBase):
    hashed_password: str
    role: str = Field("member", example="admin")

class UserPublic(BaseModel):
    id: PyObjectId = Field(alias="_id", serialization_alias="id")
    email: EmailStr
    role: str
    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# --- Modelos de Token ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Modelos de Importação ---
class ColumnMapping(BaseModel):
    from_column: str
    to_field: str

class ImportRequest(BaseModel):
    analysis_id: str
    mappings: List[ColumnMapping]

# --- Modelos de Lead ---
class LeadPublic(BaseModel):
    id: PyObjectId = Field(alias="_id", serialization_alias="id")
    # Adicione os campos que você QUER mostrar para o usuário
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    empresa: Optional[str] = None
    curso: Optional[str] = None
    # Adicione outros campos importantes que foram mapeados...

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class LeadUpdate(BaseModel):
    # Todos os campos são opcionais para permitir atualizações parciais.
    candidato_id: Optional[str] = None
    concurso: Optional[str] = None
    aluno_id: Optional[str] = None
    nome: Optional[str] = None
    curso: Optional[str] = None
    polo: Optional[str] = None
    polo_vendor: Optional[str] = None
    cod_vendor: Optional[str] = None
    vestibular: Optional[str] = None
    cod_parceiro: Optional[str] = None
    nota: Optional[float] = None
    taxa_expediente: Optional[float] = None
    mensalidade: Optional[float] = None
    aproveitamento: Optional[str] = None
    celular: Optional[str] = None
    telefone_fixo: Optional[str] = None
    email: Optional[EmailStr] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    bairro: Optional[str] = None
    cep: Optional[str] = None
    cpf: Optional[str] = None
    endereco: Optional[str] = None
    complemento: Optional[str] = None
    numero_endereco: Optional[str] = None
    mensalidade_pagamento: Optional[str] = None
    data_inscricao: Optional[str] = None
    area_de_atuacao: Optional[str] = None
    local_de_trabalho: Optional[str] = None
    como_conheceu: Optional[str] = None
    ano_conclusao_2_grau: Optional[str] = None
    inscrito_por: Optional[str] = None
    secretaria_academica_digital: Optional[str] = None
    retencao_reativa: Optional[str] = None
    tipo_ingresso_prouni: Optional[str] = None
    tipo_concurso: Optional[str] = None
    nome_curso: Optional[str] = None
    unidade: Optional[str] = None
    encrypt_candidato: Optional[str] = None

    model_config = ConfigDict(
        extra='forbid'
    )
