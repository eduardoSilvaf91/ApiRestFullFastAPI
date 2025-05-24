from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class ClientBase(BaseModel):
    name: str = Field(..., alias="nome")
    email: EmailStr
    cpf: str
    phone: str | None = Field(None, alias="telefone")
    address: str | None = Field(None, alias="endereco")
    birth_date: datetime | None = Field(None, alias="data_nascimento")
    
    class Config:
        populate_by_name = True

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: str | None = Field(..., alias="nome")
    email: EmailStr | None = None
    phone: str | None =  Field(None, alias="telefone")
    address: str | None = Field(None, alias="endereco")

class Client(ClientBase):
    id: int
    active: bool = Field(..., alias="ativo")
    created_at: datetime = Field(None, alias="criado_em")
    updated_at: datetime = Field(None, alias="atualizado_em")

    class Config:
        from_attributes = True
        
# class ClientResponse(BaseModel):
#     id: int
#     name: str = Field(..., alias="nome")
#     email: str
#     cpf: str
#     phone: str | None = Field(None, alias="telefone")
#     address: str | None = Field(None, alias="endereco")
#     birth_date: datetime | None = Field(None, alias="data_nascimento")
#     active: bool = Field(..., alias="ativo")
#     created_at: datetime = Field(..., alias="criado_em")
#     updated_at: datetime = Field(..., alias="atualizado_em")

#     class Config:
#         orm_mode = True
#         populate_by_name = True