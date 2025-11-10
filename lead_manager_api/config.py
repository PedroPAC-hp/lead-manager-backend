# backend/lead_manager_api/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # As variáveis que sua aplicação precisa.
    # O Pydantic vai tentar carregá-las de um arquivo .env automaticamente.
    MONGO_URI: str
    DATABASE_NAME: str # Adicionei para ser mais explícito
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Aponta para o arquivo .env na pasta raiz 'backend/'
    # O caminho é relativo a onde o uvicorn é executado.
    model_config = SettingsConfigDict(env_file=".env")

# Cria uma instância única das configurações que será usada em toda a aplicação.
settings = Settings()
