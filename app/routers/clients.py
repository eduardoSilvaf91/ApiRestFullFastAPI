from fastapi import APIRouter, Depends, Query, status
from typing import Annotated
from schemas.clients import (
    Client,
    ClientCreate,
    ClientUpdate,
    Address, 
    AddressCreate,
    AddressUpdate
)
from services.clients import (
    get_clients, 
    create_client, 
    get_client, 
    update_client, 
    delete_client,
)
from services.address import (
    get_addresses,
    create_address,
    update_address,
    delete_address
)
from typing import List, Optional
from dependencies import get_db, get_current_user
from connectDB.database import Usuario


router = APIRouter()

@router.get("/", response_model=list[Client])
async def list_clients(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    name: str | None = None,
    email: str | None = None,
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
    ):
    
    return await get_clients(db, skip, limit, name, email)

@router.post("/", response_model=Client, status_code=status.HTTP_201_CREATED)
async def add_client(
    client: ClientCreate,
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
    ):
    
    return await create_client(db, client)

@router.get("/{id}", response_model=Client)
async def read_client(
    id: int,
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
    ):
    
    return await get_client(db, id)

@router.put("/{id}", response_model=Client)
async def edit_client(
    id: int,
    client: ClientUpdate,
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
    ):
    
    return await update_client(db, id, client)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_client(
    id: int,
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
    ):
    
    await delete_client(db, id)

#________________________________________________________________________________

# addresses

@router.get("/{id_client}/addresses/", response_model=List[Address])
async def read_client_addresses(
    id_client: int,
    id_address: Optional[int] = None,
    is_primary_address: Optional[bool] = None,
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return await get_addresses(db, id_client, id_address, is_primary_address)


@router.post("/{id_client}/addresses/", response_model=Address, status_code=status.HTTP_201_CREATED)
async def create_client_address(
    id_client: int,
    address: AddressCreate,
    db= Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return await create_address(db, id_client, address)

@router.put("/{id_client}/addresses/{address_id}", response_model=AddressUpdate)
async def update_client_address(
    id_client: int,
    address_id: int,
    address: AddressUpdate,
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return await update_address(db, id_client, address_id, address)

@router.delete("/{client_id}/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_address(
    client_id: int,
    address_id: int,
    db= Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    await delete_address(db, client_id, address_id)