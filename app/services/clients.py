from sqlalchemy.orm import Session
from connectDB.database import Cliente, Pedido
from schemas.clients import ClientCreate, ClientUpdate
from datetime import datetime, timezone
from fastapi import HTTPException, status
import re

def validate_cpf(cpf: str):
    """Validação simples de CPF (pode ser implementada a validação real)"""
    cpf = remove_special_characters(cpf)
    
    if len(cpf) != 11 or not cpf.isdigit():
        return False
    return True

def remove_special_characters(cpf: str):
    """Remove caracteres especiais de um CPF"""
    return re.sub(r'[^0-9]', '', cpf)

async def get_clients(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    name: str | None = None,
    email: str | None = None,
    active: bool | None = None
):
    """Lista clientes com filtros"""
    query = db.query(Cliente)
    
    if name:
        query = query.filter(Cliente.nome.ilike(f"%{name}%"))
    if email:
        query = query.filter(Cliente.email.ilike(f"%{email}%"))
    if active is not None:
        query = query.filter(Cliente.ativo == active)
    
    return query.offset(skip).limit(limit).all()

async def create_client(db: Session, client: ClientCreate):
    """Cria um novo cliente com validações"""
    # Valida CPF
    if not validate_cpf(client.cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CPF"
        )
    
    # Verifica se email já existe
    existing_email = db.query(Cliente).filter(
        Cliente.email == client.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verifica se CPF já existe
    client.cpf = remove_special_characters(client.cpf)
    
    existing_cpf = db.query(Cliente).filter(
        Cliente.cpf == client.cpf
    ).first()
    if existing_cpf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF already registered"
        )
    
    db_client = Cliente(
        nome=client.name,
        email=client.email,
        cpf=client.cpf,
        telefone=client.phone,
        endereco=client.address,
        data_nascimento=client.birth_date,
        ativo=True,
        criado_em=datetime.now(timezone.utc),
        atualizado_em=datetime.now(timezone.utc)
    )
    
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

async def get_client(db: Session, id: int):
    """Obtém um cliente por ID"""
    client = db.query(Cliente).filter(Cliente.id == id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client

async def update_client(db: Session, id: int, client: ClientUpdate):
    """Atualiza um cliente existente"""
    db_client = db.query(Cliente).filter(Cliente.id == id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Atualiza apenas os campos fornecidos
    if client.name is not None:
        db_client.nome = client.name
    if client.email is not None:
        # Verifica se novo email já existe
        if client.email != db_client.email:
            existing = db.query(Cliente).filter(
                Cliente.email == client.email
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        db_client.email = client.email
    if client.phone is not None:
        db_client.telefone = client.phone
    if client.address is not None:
        db_client.endereco = client.address
    
    db_client.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_client)
    return db_client

async def delete_client(db: Session, id: int):
    """Remove um cliente (soft delete)"""
    db_client = db.query(Cliente).filter(Cliente.id == id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Verifica se cliente tem pedidos
    has_orders = db.query(Pedido).filter(
        Pedido.cliente_id == id
    ).first() is not None
    
    if has_orders:
        # Soft delete (marca como inativo)
        db_client.ativo = False
        db_client.atualizado_em = datetime.now(timezone.utc)
        db.commit()
        return {"message": "Client deactivated (has existing orders)"}
    else:
        # Delete físico (se não tiver pedidos)
        db.delete(db_client)
        db.commit()
        return {"message": "Client permanently deleted"}