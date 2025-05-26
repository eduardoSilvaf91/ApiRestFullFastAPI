from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ImageBase(BaseModel):
    url: str
    order: int = Field(..., alias="ordem")

class Image(ImageBase):
    id: int
    created_at: datetime = Field(None, alias="criado_em")
    produto_id: int = Field(..., alias="produto_id")
    criado_em: datetime = Field(None, alias="criado_em")
    
    class Config:
        from_attributes = True
 

class ProductBase(BaseModel):
    name: str = Field(..., alias="nome")
    description: str = Field(..., alias="descricao")
    sale_price: float = Field(..., alias="valor_venda")
    barcode: Optional[str] = Field(None, alias="codigo_barras")
    category_id: int = Field(..., alias="categoria_id")
    stock: int = Field(0, alias="estoque")
    min_stock: int = Field(5, alias="estoque_minimo")
    expiry_date: Optional[datetime] = Field(None, alias="data_validade")
    status: bool = Field(True, alias="ativo")

class ProductCreate(ProductBase):
    images: Optional[List[ImageBase]] = None

class ProductUpdate(BaseModel):
    name: Optional[str] | None = Field(None, alias="nome")
    description: Optional[str] | None = Field(None, alias="descricao")
    sale_price: Optional[float] | None = Field(None, alias="valor_venda")
    stock: Optional[int] | None = Field(None, alias="estoque")
    min_stock: Optional[int] | None = Field(5, alias="estoque_minimo")
    status: Optional[bool] | None = Field(None, alias="ativo")
    expiry_date: Optional[datetime] = Field(None, alias="data_validade")

class Product(ProductBase):
    id: int
    created_at: datetime = Field(None, alias="criado_em")
    updated_at: datetime = Field(None, alias="atualizado_em")
    images: List[Image] = Field([], alias="imagens")

    class Config:
        from_attributes = True
