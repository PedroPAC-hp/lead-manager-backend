# main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from lead_manager_api.database import connect_to_mongo, close_mongo_connection
from lead_manager_api.api.auth import router as auth_router
from lead_manager_api.api.config_routes import router as config_router
from lead_manager_api.api.import_routes import router as import_router # <-- Ele vai importar a versão simples

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Lead Manager API",
    description="API para gerenciamento e importação de leads.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth_router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(config_router, prefix="/api/config", tags=["Configuração de Produtos"])
app.include_router(import_router, prefix="/api/import", tags=["Importação"]) # <-- Rota de teste

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo à API Lead Manager!"}
