from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Annotated, Optional
from schemas.products import Product, ProductCreate, ProductUpdate
from services.products import (
    get_products,
    create_product,
    get_product,
    update_product,
    delete_product
)
from dependencies import get_db, get_current_user
from connectDB.database import Usuario

router = APIRouter()

@router.get("/", response_model=list[Product])
async def list_products(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    category: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return await get_products(
        db, skip, limit, 
        category, min_price, max_price, in_stock
    )

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def add_product(
    product: ProductCreate, 
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return await create_product(db, product)

@router.get("/{id}", response_model=Product)
async def read_product(
    id: int,
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)    
):
    product = await get_product(db, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{id}", response_model=Product)
async def edit_product(
    id: int, 
    product: ProductUpdate, 
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return await update_product(db, id, product)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_product(
    id: int, 
    db=Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    await delete_product(db, id)