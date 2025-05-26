# FastAPI RESTful API

API desenvolvida com FastAPI para gerenciamento de usuários, categorias, clientes, pedidos e produtos, integrada com banco de dados PostgreSQL, com autenticação JWT.

---
---

## Índice

- [Descrição](#descrição)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Execução](#execução)
- [Endpoints](#endpoints)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Docker](#docker)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## Descrição

API RESTful construída com FastAPI que oferece recursos para autenticação (login, registro, refresh token), e gerenciamento de categorias, clientes, endereços, pedidos e produtos.

---

## Funcionalidades

- Autenticação com JWT (login, registro e refresh token)
- CRUD completo para:
  - Categorias de produtos
  - Clientes e seus endereços
  - Pedidos
  - Produtos
- Filtros e paginação em listagens
- Soft delete em categorias (quando associadas a produtos)

---

## Tecnologias

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker & Docker Compose

---
## Banco de dados
![modelo conceitual](BrModelo/Conceitual.png)
![modelo lógico](BrModelo/Lógico.png)

## Instalação

### Pré-requisitos

- Docker
- Docker Compose

Clone este repositório:

```bash
git clone <seu-repositorio-url>
cd <nome-do-diretorio>
