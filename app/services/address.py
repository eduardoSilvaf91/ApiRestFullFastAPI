from sqlalchemy.orm import Session
from connectDB.database import Endereco
from schemas.clients import AddressCreate, AddressUpdate
from services.utilities import remove_special_characters
from fastapi import HTTPException, status
import re
from typing import List, Optional

#___________________________________________________
# get client_address 

async def get_addresses(
    db: Session, 
    id_client: int,
    id_address: int | None = None,
    is_primary_address: bool | None = None
) -> List[Endereco]:
    """Lista todos os endereços de um cliente"""
    

    query = db.query(Endereco).filter(Endereco.cliente_id == id_client)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço do cliente não encontrado"
        )
    # Aplica filtros opcionais
    if id_address is not None:
        query = query.filter(Endereco.id == id_address)
        if not query:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Endereço não pertence ao cliente"
            )
            
    # Verifica se é o endereço principal
    if is_primary_address is not None:
        query = query.filter(Endereco.principal == is_primary_address)
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endereço Principal não encontrado"
            )

    return query

#___________________________________________________
# post client_address 

async def create_address(
    db: Session, 
    client_id: int, 
    address: AddressCreate
) -> Endereco:
    """Cria um novo endereço para o cliente"""
    # Se for o primeiro endereço, força como principal
    existing_addresses = db.query(Endereco).filter(
        Endereco.cliente_id == client_id
    ).count()
    
    db_address = Endereco(
        cliente_id=client_id,
        logradouro=address.street,
        numero=address.number,
        complemento=address.complement,
        bairro=address.neighborhood,
        cidade=address.city,
        estado=address.state,
        cep=remove_special_characters(address.zip_code),
        principal=address.is_primary or existing_addresses == 0
    )
    
    if address.is_primary:
        # Verifica se já existe um endereço principal
        existing_primary = db.query(Endereco).filter(
            Endereco.cliente_id == client_id,
            Endereco.principal == True
        ).first()
        if existing_primary:
            existing_primary.principal = False
    
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    
    return db_address

#___________________________________________________
# update client_address 
async def update_address(
    db: Session,
    client_id: int,
    address_id: int,
    address: AddressUpdate
) -> Endereco:
    """Atualiza um endereço do cliente"""
    query = await get_addresses(db, client_id, address_id)
    db_address = query.first()
    
    # Verifica se o endereço existe
    if not db_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço não encontrado"
        )
    
    if address.street is not None:
        db_address.logradouro = address.street
    if address.number is not None:
        db_address.numero = address.number
    if address.complement is not None:
        db_address.complemento = address.complement
    if address.neighborhood is not None:
        db_address.bairro = address.neighborhood
    if address.city is not None:
        db_address.cidade = address.city
    if address.state is not None:
        db_address.estado = address.state
    if address.zip_code is not None:
        db_address.cep = address.zip_code
    if address.is_primary is not None:
        if address.is_primary:
            # Desmarca todos os outros endereços principais do cliente
            db.query(Endereco).filter(
                Endereco.cliente_id == client_id,
                Endereco.id != address_id
            ).update({Endereco.principal: False})
            db_address.principal = True
        else:
            db_address.principal = False
        
    db.commit()
    db.refresh(db_address)
    return db_address

#___________________________________________________
# delete client_address 
async def delete_address(
    db: Session,
    client_id: int,
    address_id: int
) -> None:
    """Remove um endereço do cliente"""
    
    # get 1 address
    query = await get_addresses(db, client_id, address_id)
    db_address = query.first()
    if not db_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço não encontrado"
        )
    
    # Verifica se é o último endereço
    num_addresses = db.query(Endereco).filter(Endereco.cliente_id == client_id).count()
    
    if num_addresses <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover o único endereço do cliente"
        )
    
    # Verifica se está tentando remover o endereço principal
    if db_address.principal is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover o endereço principal. Defina outro como principal primeiro."
        )

    db.delete(db_address)
    db.commit()