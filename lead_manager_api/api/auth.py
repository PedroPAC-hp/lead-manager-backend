# lead_manager_api/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import datetime, timezone
from pymongo.database import Database

from ..database import get_database
from ..schemas import UserCreate, UserPublic, Token
from ..security import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Database = Depends(get_database)):
    users_collection = db["users"]
    if users_collection.find_one({"email": user_data.email}):
        raise HTTPException(status_code=400, detail="Email já registrado.")

    hashed_password = get_password_hash(user_data.password)
    role = "admin" if users_collection.count_documents({}) == 0 else "member"

    user_to_save = {
        "email": user_data.email,
        "hashed_password": hashed_password,
        "role": role,
        "created_at": datetime.now(timezone.utc)
    }
    result = users_collection.insert_one(user_to_save)
    created_user = users_collection.find_one({"_id": result.inserted_id})
    
    # Converte ObjectId para string para o modelo Pydantic
    created_user["_id"] = str(created_user["_id"])
    return created_user

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Database = Depends(get_database)):
    user = db["users"].find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos")
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}