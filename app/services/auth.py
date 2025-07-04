from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from connectDB.database import Usuario, Pedido
from schemas.auth import TokenData, UserLogin, UserRegister
from sqlalchemy.orm import Session
import os

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(email: str, password: str, db: Session):
    user = db.query(Usuario).filter(Usuario.email == email, Usuario.ativo == True).first()
    if not user or not verify_password(password, user.senha_hash):
        return None
    return user

async def create_user(user: UserRegister, db: Session):
    
    # Verifica se usuário já existe
    db_user = db.query(Usuario).filter(Usuario.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = Usuario(
        nome=user.name,
        email=user.email,
        senha_hash=hashed_password,
        ativo=True,
        criado_em=datetime.now(timezone.utc),
        atualizado_em=datetime.now(timezone.utc)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def login_user(email: str, password: str, db: Session):
    user = await authenticate_user(email, password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

async def refresh_token_access(refresh_token: str, db: Session):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
    except InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # new access token 
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        return payload
    except InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    
async def get_user(db: Session):
    db_user = db.query(Usuario).all()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Formata cada resultado como um dicionário
    return [{
        "id": user.id,
        "nome": user.nome,
        "ativo": user.ativo
    } for user in db_user]

async def update_user(user_id: int, user_update: UserRegister, db: Session):
    db_user = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Atualiza os campos
    db_user.nome = user_update.name if user_update.name is not None else db_user.nome
    db_user.email = user_update.email if user_update.email is not None else db_user.email
    db_user.senha_hash = get_password_hash(user_update.password) if user_update.password is not None else db_user.senha_hash
    db_user.ativo = user_update.active if user_update.active is not None else db_user.ativo
    db_user.atualizado_em = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_user)
    return {"detail": "User updated successfully", "user": db_user}

async def delete_user(user_id: int, db: Session):
    db_user = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    # Verifica se o usuário existe
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Conta quantos usuários existem no total
    total_users = db.query(Usuario).count()
    
    if total_users <= 1:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the only user in the system."
        )
    
    # Verifica se o usuário possui pedidos associados
    has_orders = db.query(Pedido).filter(Pedido.usuario_id == user_id).first() is not None

    if has_orders:
        db_user.ativo = False
        db_user.atualizado_em = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_user)
        return {"detail": "User has orders. Marked as inactive."}
    else:
        db.delete(db_user)
        db.commit()
        return {"detail": "User deleted successfully"}