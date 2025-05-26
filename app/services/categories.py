from sqlalchemy.orm import Session
from connectDB.database import CategoriaProduto, Produto
from schemas.categories import CategoryCreate, CategoryUpdate
from datetime import datetime, timezone
from fastapi import HTTPException, status


def create_category_service(db: Session, category_data: CategoryCreate):
    """Cria uma nova categoria no banco de dados"""
    db_category = CategoriaProduto(
        nome=category_data.name,
        descricao=category_data.description,
        ativo=True,
        criado_em=datetime.now(timezone.utc),
        atualizado_em=datetime.now(timezone.utc)
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories_service(db: Session, skip: int = 0, limit: int = 100, active: bool | None = None):
    """Lista categorias com paginação e filtros"""
    query = db.query(CategoriaProduto)
    
    if active is not None:
        query = query.filter(CategoriaProduto.ativo == active)
        
    return query.offset(skip).limit(limit).all()

def get_category_service(db: Session, category_id: int):
    """Obtém uma categoria específica por ID"""
    category = db.query(CategoriaProduto).filter(CategoriaProduto.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    return category

def update_category_service(db: Session, id: int, category_update: CategoryUpdate):
    """Atualiza uma categoria existente"""
    category = get_category_service(db, id)

    if category_update.name is not None:
        category.nome = category_update.name
    if category_update.description is not None:
        category.descricao = category_update.description
    
    category.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(category)
    return category

def delete_category_service(db: Session, id: int):
    """Remove uma categoria (soft delete se tiver produtos associados)"""
    category = get_category_service(db, id)
    
    # Verifica se existem produtos associados
    has_products = db.query(Produto).filter(Produto.categoria_id == id).first() is not None
    
    if has_products:
        # Soft delete
        category.ativo = False
        category.atualizado_em = datetime.now(timezone.utc)
        db.commit()
        return {"message": "Categoria desativada (possui produtos associados)"}
    else:
        # Delete físico
        db.delete(category)
        db.commit()
        return {"message": "Categoria removida permanentemente"}