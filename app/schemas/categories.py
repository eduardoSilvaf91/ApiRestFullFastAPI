from pydantic import BaseModel, Field
from datetime import datetime

class CategoryBase(BaseModel):
    name: str = Field(..., alias="nome")
    description: str | None = Field(..., alias="descricao")

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: str | None = Field(..., alias="nome")
    description: str | None = Field(..., alias="descricao")
    

class Category(CategoryBase):
    id: int
    active: bool = Field(..., alias="ativo")
    created_at: datetime = Field(None, alias="criado_em")
    updated_at: datetime | None = Field(None, alias="atualizado_em")

    class Config:
        from_attributes = True
        