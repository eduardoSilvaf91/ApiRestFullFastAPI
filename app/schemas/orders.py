from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from schemas.products import Product

class OrderStatus(str, Enum):
    PENDING = "Pendente"
    PROCESSING = "Processando"
    SHIPPED = "Enviado"
    DELIVERED = "Entregue"
    CANCELLED = "Cancelado"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "Cartão de Crédito"
    DEBIT_CARD = "Cartão de Débito"
    BOLETO = "Boleto"
    PIX = "Pix"
    CASH = "Dinheiro"

class OrderItemBase(BaseModel):
    product_id: int = Field(...,alias="produto_id",description="ID do produto")
    quantity: int = Field(..., gt=0, alias="quantidade", description="Quantidade do item (deve ser maior que 0)")
    unit_price: float = Field(..., ge=0,alias="preco_unitario", description="Preço unitário do produto")
    discount: float = Field(default=0.0, ge=0, alias="desconto", description="Desconto aplicado ao item")

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int = Field(..., description="ID do item do pedido")
    total: float = Field(..., ge=0, alias="total_item", description="Total do item (quantidade x preço unitário - desconto)")
    product: Product = Field(..., alias="produto", description="Produto relacionado")

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    client_id: int = Field(..., alias="cliente_id", description="ID do cliente")
    payment_method: PaymentMethod = Field(..., alias="metodo_pagamento", description="Método de pagamento")
    shipping_address: str = Field(..., alias="endereco_entrega", description="Endereço de entrega")
    notes: Optional[str] = Field(None, alias="observacoes", description="Observações sobre o pedido")
    expected_delivery_date: Optional[datetime] = Field(None, alias="data_entrega_prevista", description="Data de entrega prevista")

class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., alias="itens_pedido", description="Itens do pedido")

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = Field(None, alias="status", description="Status do pedido")
    payment_method: Optional[PaymentMethod] = Field(None, alias="metodo_pagamento", description="Método de pagamento")
    shipping_address: Optional[str] = Field(None, alias="endereco_entrega", description="Endereço de entrega")

class Order(OrderBase):
    id: int = Field(..., description="ID do pedido")
    user_id: int = Field(..., alias="usuario_id", description="ID do usuário")
    status: OrderStatus = Field(..., alias="status", description="Status do pedido")
    total: float = Field(..., ge=0, alias="valor_total", description="Total do pedido")
    discount: float = Field(default=0.0, ge=0, alias="valor_desconto", description="Desconto aplicado ao pedido")
    shipping_cost: float = Field(default=0.0, ge=0, alias="valor_frete", description="Custo de frete")
    created_at: datetime = Field(..., alias="criado_em", description="Data de criação do pedido")
    updated_at: datetime = Field(..., alias="atualizado_em", description="Data de atualização do pedido")
    items: List[OrderItem] = Field(..., alias="itens", description="Itens do pedido")

    class Config:
        from_attributes = True