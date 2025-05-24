from sqlalchemy.orm import Session
from connectDB.database import Pedido, ItemPedido, Produto, Cliente, Usuario
from schemas.orders import OrderCreate, OrderUpdate, OrderStatus, PaymentMethod
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, status
from typing import List

async def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    category: int | None = None,
    order_id: int | None = None,
    status: str | None = None,
    client_id: int | None = None,
    user_id: int | None = None
):
    """Lista pedidos com filtros avançados"""
    query = db.query(Pedido)
    
    # Aplicar filtros
    if order_id:
        query = query.filter(Pedido.id == order_id)
    if client_id:
        query = query.filter(Pedido.cliente_id == client_id)
    if user_id:
        query = query.filter(Pedido.usuario_id == user_id)
    if status:
        query = query.filter(Pedido.status == status)
    if start_date:
        query = query.filter(Pedido.criado_em >= start_date)
    if end_date:
        query = query.filter(Pedido.criado_em <= end_date)
    if category:
        query = query.join(ItemPedido).join(Produto).filter(
            Produto.categoria_id == category
        )
    
    return query.order_by(Pedido.criado_em.desc()).offset(skip).limit(limit).all()

async def create_order(db: Session, order: OrderCreate, user_id: int):
    """Cria um novo pedido com validação de estoque"""
    # Validações iniciais
    if not order.items or len(order.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must have at least one item"
        )
    
    # Verifica se cliente existe
    client = db.query(Cliente).filter(Cliente.id == order.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client not found"
        )
    
    # Prepara itens e calcula totais
    order_items = []
    total = Decimal('0.00')
    shipping_cost = Decimal('0.00')  # Poderia ser calculado com base em regras de negócio
    
    # Valida cada item do pedido
    for item in order.items:
        product = db.query(Produto).filter(Produto.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item.product_id} not found"
            )
        
        if not product.ativo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.nome} is inactive"
            )
        
        if product.estoque < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.nome}. Available: {product.estoque}"
            )
        
        # Calcula total do item
        item_total = Decimal(str(item.unit_price)) * item.quantity - Decimal(str(item.discount))
        total += item_total
        
        order_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "discount": item.discount,
            "total": float(item_total)
        })
    
    # Cria o pedido no banco de dados
    db_order = Pedido(
        cliente_id=order.client_id,
        usuario_id=user_id,
        status=OrderStatus.PENDING.value,
        valor_total=float(total),
        valor_desconto=0.00,  # Poderia ser calculado com cupons, etc.
        valor_frete=float(shipping_cost),
        metodo_pagamento=order.payment_method.value,
        observacoes=order.notes,
        endereco_entrega=order.shipping_address,
        data_entrega_prevista=order.expected_delivery_date,
        criado_em=datetime.now(timezone.utc),
        atualizado_em=datetime.now(timezone.utc)
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Adiciona itens do pedido e atualiza estoque
    for item in order_items:
        # Cria item do pedido
        db_item = ItemPedido(
            pedido_id=db_order.id,
            produto_id=item["product"].id,
            quantidade=item["quantity"],
            preco_unitario=item["unit_price"],
            desconto=item["discount"],
            total_item=item["total"]
        )
        db.add(db_item)
        
        # Atualiza estoque do produto
        item["product"].estoque -= item["quantity"]
        item["product"].atualizado_em = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_order)
    return db_order

async def get_order(db: Session, id: int):
    """Obtém um pedido específico por ID"""
    order = db.query(Pedido).filter(Pedido.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

async def update_order(db: Session, id: int, order: OrderUpdate):
    """Atualiza um pedido existente"""
    db_order = db.query(Pedido).filter(Pedido.id == id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Valida transições de status
    if order.status:
        current_status = db_order.status
        new_status = order.status.value
        
        # Valida se a transição de status é permitida
        valid_transitions = {
            OrderStatus.PENDING.value: [OrderStatus.PROCESSING.value, OrderStatus.CANCELLED.value],
            OrderStatus.PROCESSING.value: [OrderStatus.SHIPPED.value, OrderStatus.CANCELLED.value],
            OrderStatus.SHIPPED.value: [OrderStatus.DELIVERED.value],
            # Outras transições...
        }
        
        if (current_status in valid_transitions and 
            new_status not in valid_transitions[current_status]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from {current_status} to {new_status}"
            )
        
        db_order.status = new_status
    
    # Atualiza outros campos se fornecidos
    if order.payment_method:
        db_order.metodo_pagamento = order.payment_method.value
    if order.shipping_address:
        db_order.endereco_entrega = order.shipping_address
    
    db_order.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_order)
    return db_order

async def delete_order(db: Session, id: int):
    """Cancela/remove um pedido"""
    db_order = db.query(Pedido).filter(Pedido.id == id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Se o pedido já foi enviado, não pode ser cancelado
    if db_order.status in [OrderStatus.SHIPPED.value, OrderStatus.DELIVERED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel an order that has already been shipped or delivered"
        )
    
    # Restaura estoque dos produtos
    for item in db_order.itens:
        product = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if product:
            product.estoque += item.quantidade
            product.atualizado_em = datetime.now(timezone.utc)
    
    # Atualiza status para cancelado
    db_order.status = OrderStatus.CANCELLED.value
    db_order.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    
    return {"message": "Order cancelled successfully"}