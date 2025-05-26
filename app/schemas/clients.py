from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional


# Schemas para Endereço
class AddressBase(BaseModel):
    street: str = Field(..., alias="logradouro")
    number: str = Field(..., alias="numero")
    complement: Optional[str] = Field(None, alias="complemento")
    neighborhood: str = Field(..., alias="bairro")
    city: str = Field(..., alias="cidade")
    state: str = Field(..., alias="estado", min_length=2, max_length=2)
    zip_code: str = Field(..., alias="cep")
    is_primary: bool = Field(True, alias="principal")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class AddressCreate(AddressBase):
    pass

class Address(AddressBase):
    id: int
    cliente_id: int

class AddressUpdate(BaseModel):
    street: Optional[str] = Field(None, alias="logradouro")
    number: Optional[str] = Field(None, alias="numero")
    complement: Optional[str] = Field(None, alias="complemento")
    neighborhood: Optional[str] = Field(None, alias="bairro")
    city: Optional[str] = Field(None, alias="cidade")
    state: Optional[str] = Field(None, alias="estado", min_length=2, max_length=2)
    zip_code: Optional[str] = Field(None, alias="cep")
    is_primary: Optional[bool] = Field(None, alias="principal")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

# Schemas para Cliente
class ClientBase(BaseModel):
    first_name: str = Field(..., alias="nome", min_length=2, max_length=50)
    last_name: str = Field(..., alias="sobrenome", min_length=2, max_length=50)
    email: EmailStr
    cpf: str = Field(..., min_length=11, max_length=11)
    phone: str | None = Field(None, alias="telefone", max_length=20)
    birth_date: datetime | None = Field(None, alias="data_nascimento")
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class ClientCreate(ClientBase):
    addresses: List[AddressCreate] = Field(alias="enderecos",default_factory=list)

class ClientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, alias="nome", min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, alias="sobrenome", min_length=2, max_length=50)
    email: EmailStr | None = None
    phone: str | None =  Field(None, alias="telefone", max_length=20)
    birth_date: Optional[date] = Field(None, alias="data_nascimento")
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class Client(ClientBase):
    id: int
    active: bool = Field(..., alias="ativo")
    created_at: datetime = Field(None, alias="criado_em")
    updated_at: datetime = Field(None, alias="atualizado_em")
    addresses: List[Address] = Field(alias="enderecos",default_factory=list)
    class Config:
        from_attributes = True
        



