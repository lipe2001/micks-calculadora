# Micks Calculadora — Desafio Técnico

Aplicação completa (API + WEB) para **calcular e contratar** plano de internet por quantidade de dispositivos.  
Arquitetura em **monorepo**, orquestrada por **Docker Compose** (Windows + Docker Desktop).

## Stack & Portas
- **API (3000):** Python 3.12, FastAPI, Pydantic, SQLAlchemy 2.x, Alembic, Uvicorn
- **WEB (3001):** FastAPI + Jinja2 + HTMX (consome a API)
- **Banco:** PostgreSQL (Docker)
- **E-mail (dev):** MailHog (Docker) — UI em `http://localhost:8025`
- **Rotas principais:** `/calculadora_plano` e `/vendas` (login: **admin** / senha: **desafio**)

## Como rodar (Windows + Docker Desktop)
> Pré-requisito: Docker Desktop em **Running** e WSL2 habilitado.

```powershell
# 1) Clonar e entrar na pasta
git clone https://github.com/lipe2001/micks-calculadora.git
cd micks-calculadora

# 2) Criar o arquivo de variáveis de ambiente
Copy-Item .\infra\.env.example .\infra\.env

# 3) Build e subir os serviços
docker compose -f .\infra\docker-compose.yml build
docker compose -f .\infra\docker-compose.yml up -d

# 4) Rodar as migrações (cria tabela sales)
docker compose -f .\infra\docker-compose.yml run --rm api alembic upgrade head
