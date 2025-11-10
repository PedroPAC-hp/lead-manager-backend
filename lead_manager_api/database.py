# backend/lead_manager_api/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings # Importa as configurações

client: AsyncIOMotorClient = None

async def connect_to_mongo():
    global client
    print("Conectando ao MongoDB...")
    client = AsyncIOMotorClient(settings.MONGO_URI)
    print("Conexão com MongoDB estabelecida.")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Conexão com MongoDB fechada.")

def get_database():
    if client is None:
        raise Exception("A conexão com o banco de dados não foi estabelecida.")
    # Usa o nome do banco de dados das nossas configurações
    return client[settings.DATABASE_NAME]
