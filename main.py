# backend/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from lead_manager_api.database import connect_to_mongo, close_mongo_connection
from lead_manager_api.api.auth import router as auth_router
from lead_manager_api.api.import_routes import router as import_router
from lead_manager_api.api import auth_router, import_router, config_router
from fastapi.middleware.cors import CORSMiddleware

# Usando o novo 'lifespan' para gerenciar a conexão com o banco
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código a ser executado na inicialização
    await connect_to_mongo()
    yield
    # Código a ser executado no encerramento
    await close_mongo_connection()

# Cria a instância da aplicação FastAPI com o gerenciador de ciclo de vida
app = FastAPI(
    title="Lead Manager API",
    description="API para gerenciamento e importação de leads.",
    version="1.0.0",
    lifespan=lifespan
)

# Inclui os roteadores da sua aplicação
# Damos um "apelido" para cada router na hora de importar para evitar conflito de nomes
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

# 2. Adicione a nova linha para incluir as rotas de configuração
app.include_router(auth_router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(import_router, prefix="/api/import", tags=["Importação de Leads"])
app.include_router(config_router, prefix="/api/config/products", tags=["Configuração de Produtos"]) # <-- ADICIONE ESTA LINHA

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo à API Lead Manager!"}