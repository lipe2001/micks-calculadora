# Micks Calculadora — Desafio Técnico

Monorepo para a **Calculadora de Plano de Internet** (Frontend + Backend) com Docker Compose.

## Stack & Portas
- **API (3000):** Python 3.12 + FastAPI + Pydantic + SQLAlchemy 2.x + Alembic + Uvicorn
- **WEB (3001):** FastAPI servindo templates **Jinja2** + **HTMX**
- **Banco:** **PostgreSQL** (Docker)
- **E-mail (dev):** **MailHog** (Docker)
- **Orquestração:** **Docker Compose**
- **Rotas-chave:** `/calculadora_plano`, `/vendas` (login: admin / senha: desafio)

## Estrutura
```
micks-calculadora/
  apps/
    api/   # FastAPI API (porta 3000)
    web/   # FastAPI + Jinja2 + HTMX (porta 3001)
  infra/   # docker-compose e configs
```

## Como rodar (resumo)
1. Copie `infra/.env.example` para `infra/.env` (ajuste se quiser).
2. No terminal, na raiz do projeto:
   ```powershell
   docker compose -f .\infra\docker-compose.yml build --no-cache
   docker compose -f .\infra\docker-compose.yml up -d
   docker compose -f .\infra\docker-compose.yml run --rm api alembic upgrade head
   ```
3. Testes:
   - API: http://localhost:3000/health
   - WEB: http://localhost:3001/health
   - MailHog: http://localhost:8025
4. Banco: Postgres exposto em `localhost:5432` (user/db/pass: `micks`).

> **Importante:** Não commite `infra/.env`. Use o `.env.example` no Git.