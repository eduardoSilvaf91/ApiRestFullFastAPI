from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Annotated, Optional
from datetime import datetime
from schemas.orders import Order, OrderCreate, OrderUpdate
from services.orders import (
    get_orders,
    create_order,
    get_order,
    update_order,
    delete_order
)
from dependencies import get_db, get_current_user
from connectDB.database import Usuario

router = APIRouter()

@router.get("/", response_model=list[Order])
async def list_orders(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[int] = None,
    order_id: Optional[int] = None,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return await get_orders(
        db, skip, limit, 
        start_date, end_date, 
        category, order_id, 
        status, client_id
    )

@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def add_order(
    order: OrderCreate, 
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
    
):
    return await create_order(db, order, current_user.id)
    # return await create_order(db, order, 1)  # Temporarily using 1 as user ID for testing
    

@router.get("/{id}", response_model=Order)
async def read_order(
    id: int,
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    order = await get_order(db, id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{id}", response_model=Order)
async def edit_order(
    id: int, 
    order: OrderUpdate, 
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return await update_order(db, id, order)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_order(
    id: int, 
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    await delete_order(db, id)