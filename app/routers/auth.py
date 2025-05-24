from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.auth import Token, UserLogin, UserRegister
from sqlalchemy.orm import Session
from services.auth import login_user, create_user, refresh_token_access
from typing import Annotated
from dependencies import get_db, get_current_user
from connectDB.database import Usuario

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    return await login_user(form_data.username, form_data.password, db)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserRegister,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
    ):
    return await create_user(user, db)

@router.post("/refresh-token", response_model=Token)
async def refresh(
    refresh_token: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)    
    ):
    return await refresh_token_access(refresh_token, db)
