# lead_manager_api/database.py
import pymongo
from .config import settings

client = None

def connect_to_mongo():
    global client
    print("Conectando ao MongoDB (síncrono)...")
    client = pymongo.MongoClient(settings.MONGO_URI)
    print("Conexão com MongoDB (síncrono) estabelecida.")

def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Conexão com MongoDB (síncrono) fechada.")

def get_database():
    if client is None:
        connect_to_mongo()
    return client[settings.DATABASE_NAME]