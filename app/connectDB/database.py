from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Numeric, Enum, CheckConstraint
)
from datetime import datetime, timezone
import enum
import os

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "fastapi_db")

# Configuração do banco de dados
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Enums
class StatusPedido(str, enum.Enum):
    PENDENTE = "Pendente"
    PROCESSANDO = "Processando"
    ENVIADO = "Enviado"
    ENTREGUE = "Entregue"
    CANCELADO = "Cancelado"

class MetodoPagamento(str, enum.Enum):
    CARTAO_CREDITO = "Cartão de Crédito"
    CARTAO_DEBITO = "Cartão de Débito"
    BOLETO = "Boleto"
    PIX = "Pix"
    DINHEIRO = "Dinheiro"

# Modelos
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    pedidos = relationship("Pedido", back_populates="usuario")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    cpf = Column(String(11), unique=True, nullable=False)
    telefone = Column(String(20))
    endereco = Column(String(200))
    data_nascimento = Column(DateTime)
    criado_em = Column(DateTime, default=datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    pedidos = relationship("Pedido", back_populates="cliente")

class CategoriaProduto(Base):
    __tablename__ = "categorias_produto"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(200))
    ativo = Column(Boolean, default=True)

    produtos = relationship("Produto", back_populates="categoria")

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(200), nullable=False)
    valor_venda = Column(Numeric(10, 2), nullable=False)
    codigo_barras = Column(String(50), unique=True)
    categoria_id = Column(Integer, ForeignKey("categorias_produto.id"))
    estoque = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=5)
    data_validade = Column(DateTime)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    categoria = relationship("CategoriaProduto", back_populates="produtos")
    imagens = relationship("ImagemProduto", back_populates="produto")
    itens_pedido = relationship("ItemPedido", back_populates="produto")

    __table_args__ = (
        CheckConstraint('estoque >= 0', name='check_estoque_positivo'),
        CheckConstraint('estoque_minimo >= 0', name='check_estoque_minimo_positivo'),
    )

class ImagemProduto(Base):
    __tablename__ = "imagens_produto"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    url = Column(String(255), nullable=False)
    ordem = Column(Integer)
    criado_em = Column(DateTime, default=datetime.now(timezone.utc))

    produto = relationship("Produto", back_populates="imagens")

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    status = Column(Enum(StatusPedido), default=StatusPedido.PENDENTE, nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    valor_desconto = Column(Numeric(10, 2), default=0.00)
    valor_frete = Column(Numeric(10, 2), default=0.00)
    metodo_pagamento = Column(Enum(MetodoPagamento))
    observacoes = Column(String(500))
    endereco_entrega = Column(String(200))
    data_entrega_prevista = Column(DateTime)
    criado_em = Column(DateTime, default=datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    cliente = relationship("Cliente", back_populates="pedidos")
    usuario = relationship("Usuario", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    desconto = Column(Numeric(10, 2), default=0.00)
    total_item = Column(Numeric(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_pedido")

    __table_args__ = (
        CheckConstraint('quantidade > 0', name='check_quantidade_positiva'),
        CheckConstraint('preco_unitario >= 0', name='check_preco_positivo'),
    )

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True)
    expirado_em = Column(DateTime)

# Função para criar o banco de dados
def init_db():
    Base.metadata.create_all(bind=engine)

# Função para obter sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()