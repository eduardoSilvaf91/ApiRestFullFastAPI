from sqlalchemy.orm import Session
from connectDB.database import Produto, ImagemProduto, CategoriaProduto, ItemPedido
from schemas.products import ProductCreate, ProductUpdate, ProductStatus
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException, status

async def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    active: bool | None = None
):
    """Lista produtos com filtros avançados"""
    query = db.query(Produto)
    
    # Aplicar filtros
    if category:
        query = query.filter(Produto.categoria_id == category)
    if min_price is not None:
        query = query.filter(Produto.valor_venda >= min_price)
    if max_price is not None:
        query = query.filter(Produto.valor_venda <= max_price)
    if in_stock is not None:
        if in_stock:
            query = query.filter(Produto.estoque > 0)
        else:
            query = query.filter(Produto.estoque <= 0)
    if active is not None:
        query = query.filter(Produto.ativo == active)
    
    return query.offset(skip).limit(limit).all()

async def create_product(db: Session, product: ProductCreate):
    """Cria um novo produto com validações"""
    # Verifica se categoria existe
    category = db.query(CategoriaProduto).filter(
        CategoriaProduto.id == product.category_id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )
    
    # Verifica se código de barras é único (se fornecido)
    if product.barcode:
        existing = db.query(Produto).filter(
            Produto.codigo_barras == product.barcode
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Barcode already exists"
            )
    
    # Converte status para booleano (ativo/inativo)
    is_active = product.status == ProductStatus.ACTIVE
    
    # Cria o produto
    db_product = Produto(
        nome=product.name,
        descricao=product.description,
        valor_venda=product.sale_price,
        codigo_barras=product.barcode,
        categoria_id=product.category_id,
        estoque=product.stock,
        estoque_minimo=product.min_stock,
        data_validade=product.expiry_date,
        ativo=is_active,
        criado_em=datetime.now(timezone.utc),
        atualizado_em=datetime.now(timezone.utc)
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Adiciona imagens se existirem
    if product.images and len(product.images) > 0:
        for img in product.images:
            db_image = ImagemProduto(
                produto_id=db_product.id,
                url=img.url,
                ordem=img.order,
                criado_em=datetime.now(timezone.utc)
            )
            db.add(db_image)
        db.commit()
    
    return db_product

async def get_product(db: Session, id: int):
    """Obtém um produto específico por ID"""
    product = db.query(Produto).filter(Produto.id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

async def update_product(db: Session, id: int, product: ProductUpdate):
    """Atualiza um produto existente"""
    db_product = db.query(Produto).filter(Produto.id == id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Atualiza apenas os campos fornecidos
    if product.name is not None:
        db_product.nome = product.name
    if product.description is not None:
        db_product.descricao = product.description
    if product.sale_price is not None:
        db_product.valor_venda = product.sale_price
    if product.stock is not None:
        db_product.estoque = product.stock
    if product.min_stock is not None:
        db_product.estoque_minimo = product.min_stock
    if product.status is not None:
        db_product.ativo = product.status == ProductStatus.ACTIVE
    if product.expiry_date is not None:
        db_product.data_validade = product.expiry_date
    
    db_product.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_product)
    return db_product

async def delete_product(db: Session, id: int):
    """Remove um produto (soft delete ou físico)"""
    db_product = db.query(Produto).filter(Produto.id == id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Verifica se o produto está em algum pedido
    has_orders = db.query(ItemPedido).filter(
        ItemPedido.produto_id == id
    ).first() is not None
    
    if has_orders:
        # Soft delete (marca como inativo)
        db_product.ativo = False
        db_product.atualizado_em = datetime.now(timezone.utc)
        db.commit()
        return {"message": "Product deactivated (has existing orders)"}
    else:
        # Delete físico (se não tiver pedidos)
        db.delete(db_product)
        db.commit()
        return {"message": "Product permanently deleted"}

async def update_product_stock(db: Session, product_id: int, quantity_change: int):
    """Atualiza o estoque de um produto (usado ao processar pedidos)"""
    product = await get_product(db, product_id)
    
    new_stock = product.estoque + quantity_change
    if new_stock < 0:
        raise ValueError("Insufficient stock available")
    
    product.estoque = new_stock
    product.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(product)
    return product

async def check_product_availability(db: Session, product_id: int, quantity: int):
    """Verifica se um produto está disponível na quantidade solicitada"""
    product = await get_product(db, product_id)
    if not product.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is inactive"
        )
    if product.estoque < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product.estoque}"
        )
    return True
