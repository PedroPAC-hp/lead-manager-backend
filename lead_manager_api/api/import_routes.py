# backend/lead_manager_api/api/import_routes.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from typing import Annotated, List, Dict, Optional
import pandas as pd
import io
import numpy as np
import uuid
from bson import ObjectId

from ..security import get_current_active_user
from ..schemas import UserPublic, ImportRequest, LeadPublic, LeadUpdate # <-- MUDANÇA AQUI
from ..database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

ANALYSIS_CACHE: Dict[str, pd.DataFrame] = {}

@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze_spreadsheet(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    file: UploadFile = File(...)
):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Envie um .xlsx")
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        df.columns = df.columns.str.strip()
        analysis_id = str(uuid.uuid4())
        ANALYSIS_CACHE[analysis_id] = df
        column_names = list(df.columns)
        preview_df = df.head(5).replace({np.nan: None})
        preview_data = preview_df.to_dict(orient='records')
        return {
            "message": "Arquivo analisado com sucesso.",
            "analysis_id": analysis_id,
            "columns": column_names,
            "preview": preview_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {e}")

@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_mapped_data(
    import_request: ImportRequest,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    analysis_id = import_request.analysis_id
    if analysis_id not in ANALYSIS_CACHE:
        raise HTTPException(status_code=404, detail="Análise não encontrada ou expirada.")
    df = ANALYSIS_CACHE[analysis_id]
    rename_map = {m.from_column: m.to_field for m in import_request.mappings}
    for from_col in rename_map.keys():
        if from_col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Coluna '{from_col}' não encontrada.")
    df.rename(columns=rename_map, inplace=True)
    final_columns = list(rename_map.values())
    df_final = df[final_columns]
    df_final.replace({np.nan: None}, inplace=True)
    leads_to_save = df_final.to_dict(orient='records')
    if not leads_to_save:
        raise HTTPException(status_code=400, detail="Nenhum dado para importar.")
    result = await db.leads.insert_many(leads_to_save)
    del ANALYSIS_CACHE[analysis_id]
    return {"message": "Importação concluída!", "leads_salvos_no_db": len(result.inserted_ids)}

@router.get("/leads", response_model=List[LeadPublic])
async def list_leads(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    db: AsyncIOMotorDatabase = Depends(get_database),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    nome: Optional[str] = Query(None),
    email: Optional[str] = Query(None)
):
    skip = (page - 1) * limit
    query_filter = {}
    if nome:
        query_filter["nome"] = {"$regex": nome, "$options": "i"}
    if email:
        query_filter["email"] = {"$regex": f"^{email}$", "$options": "i"}
    leads_cursor = db.leads.find(query_filter).skip(skip).limit(limit)
    leads = await leads_cursor.to_list(length=limit)
    return leads

@router.put("/leads/{lead_id}", response_model=LeadPublic)
async def update_lead(
    lead_id: str,
    lead_update: LeadUpdate,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Atualiza um lead existente no banco de dados.
    O usuário precisa estar autenticado.
    """
    if not ObjectId.is_valid(lead_id):
        raise HTTPException(status_code=400, detail=f"ID do lead inválido: {lead_id}")

    update_data = lead_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo fornecido para atualização.")

    result = await db.leads.update_one(
        {"_id": ObjectId(lead_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Lead com ID {lead_id} não encontrado.")

    # --- AQUI ESTÁ A CORREÇÃO ---
    # Busca o documento completo e atualizado do banco.
    updated_lead_dict = await db.leads.find_one({"_id": ObjectId(lead_id)})
    
    # Converte o dicionário do banco de dados em uma instância do modelo Pydantic.
    # Isso garante que a resposta tenha o formato correto, com "id" em vez de "_id".
    return LeadPublic(**updated_lead_dict)

@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: str,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Deleta um lead existente do banco de dados.
    O usuário precisa estar autenticado.
    """
    # 1. Validação do ID
    if not ObjectId.is_valid(lead_id):
        raise HTTPException(status_code=400, detail=f"ID do lead inválido: {lead_id}")

    # 2. Operação no Banco de Dados
    # Tenta deletar o documento com o _id correspondente.
    result = await db.leads.delete_one({"_id": ObjectId(lead_id)})

    # 3. Verificação e Resposta
    # Se o 'deleted_count' for 0, significa que nenhum documento com aquele ID foi encontrado.
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Lead com ID {lead_id} não encontrado.")

    # Se a exclusão for bem-sucedida, a API retorna uma resposta 204 No Content,
    # que é o padrão para operações de DELETE bem-sucedidas que não precisam
    # retornar nenhum corpo de mensagem. O FastAPI cuida disso automaticamente.
    return