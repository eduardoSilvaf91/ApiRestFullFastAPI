from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, clients, products, orders
from connectDB.database import init_db


app = FastAPI(title="E-commerce API", version="1.0.0")

# Função para criar o banco de dados
init_db()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(clients.router, prefix="/clients", tags=["Clientes"])
app.include_router(products.router, prefix="/products", tags=["Produtos"])
app.include_router(orders.router, prefix="/orders", tags=["Pedidos"])
