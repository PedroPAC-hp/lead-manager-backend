# backend/lead_manager_api/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import datetime

from ..database import get_database
from ..schemas import UserCreate, UserPublic, Token # <-- MUDANÇA AQUI
from ..security import get_password_hash, verify_password, create_access_token
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    users_collection = db["users"]
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já registrado.")

    hashed_password = get_password_hash(user_data.password)
    total_users = await users_collection.count_documents({})
    role = "admin" if total_users == 0 else "member"

    user_to_save = {
        "email": user_data.email,
        "hashed_password": hashed_password,
        "role": role,
        "created_at": datetime.utcnow()
    }

    result = await users_collection.insert_one(user_to_save)
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    return created_user

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    user = await db["users"].find_one({"email": form_data.username})

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}
