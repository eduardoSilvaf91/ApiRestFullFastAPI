from sqlalchemy.orm import Session
from connectDB.database import Cliente, Endereco, Pedido
from schemas.clients import ClientCreate, ClientUpdate, AddressCreate
from services.address import get_addresses, create_address
from services.utilities import remove_special_characters, validate_cpf
from datetime import datetime, timezone, date
from fastapi import HTTPException, status

from typing import List

async def get_clients(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    name: str | None = None,
    email: str | None = None,
    active: bool | None = None,
    city: str | None = None
):
    """Lista clientes com filtros"""
    query = db.query(Cliente)
    
    if name:
        query = query.filter((Cliente.nome.ilike(f"%{name}%")) | (Cliente.sobrenome.ilike(f"%{name}%")))
    if email:
        query = query.filter(Cliente.email.ilike(f"%{email}%"))
    if active is not None:
        query = query.filter(Cliente.ativo == active)
        
    if city:
        query = query.join(Endereco).filter(
            Endereco.cidade.ilike(f"%{city}%"),
            Endereco.principal == True
        )
    
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
        Cliente.email == client.email).first()
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
        nome=client.first_name,
        sobrenome=client.last_name,
        email=client.email,
        cpf=client.cpf,
        telefone=client.phone,
        data_nascimento=client.birth_date,
        ativo=True,
        criado_em=datetime.now(timezone.utc),
        atualizado_em=datetime.now(timezone.utc)
    )
    
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    
    if client.addresses and len(client.addresses) > 0:
        
        for address in client.addresses:
            
            data = AddressCreate(
                street=address.street,
                number=address.number,
                complement=address.complement,
                neighborhood=address.neighborhood,
                city=address.city,
                state=address.state,
                zip_code=address.zip_code,
                is_primary=address.is_primary
            )
            
            # Cria cada endereço usando a função existente
            await create_address(db, db_client.id, data)
        
        db.refresh(db_client)
    
    return db_client
    
    
    
    
    
    # Adiciona endereços se fornecidos
    if client.addresses:
        await get_addresses(db, db_client.id, client.addresses)
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
    if client.first_name is not None:
        db_client.nome = client.first_name
    if client.last_name is not None:
        db_client.sobrenome = client.last_name
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
        
        # Remove endereços primeiro
        db.query(Endereco).filter(Endereco.cliente_id == id).delete()
        # Delete físico do cliente
        db.delete(db_client)
        db.commit()
        return {"message": "Client permanently deleted"}