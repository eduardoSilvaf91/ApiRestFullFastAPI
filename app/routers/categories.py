from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from schemas.categories import Category, CategoryCreate, CategoryUpdate
from services.categories import (
    create_category_service,
    get_categories_service,
    get_category_service,
    update_category_service,
    delete_category_service
)
from dependencies import get_db, get_current_user
from connectDB.database import Usuario

router = APIRouter()

@router.post(
    "/",
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova categoria",
    description="Cria uma nova categoria de produtos no sistema."
)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return create_category_service(db, category)

@router.get(
    "/",
    response_model=List[Category],
    summary="Lista todas as categorias",
    description="Retorna uma lista paginada de categorias de produtos."
)
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return get_categories_service(db, skip, limit, active)

@router.get(
    "/{id}",
    response_model=Category,
    summary="Obtém uma categoria específica",
    description="Retorna os detalhes de uma categoria pelo seu ID."
)
async def read_category(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return get_category_service(db, id)

@router.put(
    "/{id}",
    response_model=Category,
    summary="Atualiza uma categoria",
    description="Atualiza os dados de uma categoria existente."
)
async def update_category(
    id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return update_category_service(db, id, category_update)

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove uma categoria",
    description="Remove uma categoria do sistema (soft delete se houver produtos associados)."
)
async def delete_category(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    delete_category_service(db, id)