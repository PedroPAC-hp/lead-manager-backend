# main.py
from fastapi import FastAPI
from lead_manager_api.database import connect_to_mongo, close_mongo_connection
from lead_manager_api.api.auth import router as auth_router
# ... (importe os outros routers se precisar deles depois)

def startup_event():
    connect_to_mongo()

def shutdown_event():
    close_mongo_connection()

app = FastAPI(title="Lead Manager API")
app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)

app.include_router(auth_router, prefix="/api/auth", tags=["Autenticação"])
# ...

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API Lead Manager! (Versão Síncrona)"}
