# Micks Calculadora — Desafio Técnico

Monorepo para a **Calculadora de Plano de Internet** (Frontend + Backend), orquestrado por Docker Compose.

## Stack & Portas
- **API (3000):** Python 3.12 + FastAPI + Pydantic + SQLAlchemy 2.x + Alembic + Uvicorn  
- **WEB (3001):** FastAPI servindo templates **Jinja2** + **HTMX** (consome a API)  
- **Banco:** **PostgreSQL** (Docker)  
- **E-mail (dev):** **MailHog** (Docker)  
- **Orquestração:** **Docker Compose**  

## Rotas e Funcionalidades (resumo)
- **Frontend**
  - `/calculadora_plano`: formulário de dispositivos + checkbox “Cliente Gamer”, integra com `/api/calculate` (HTMX).
  - `/vendas`: lista de vendas (login obrigatório).
- **Backend**
  - `POST /api/calculate`: recebe dispositivos + gamer, calcula pesos e plano.
  - `POST /api/contract`: recebe dados do cliente + recálculo, persiste no banco e envia e-mails (cliente e operações).
  - `GET /api/sales` (autenticado): lista vendas com filtros/ordenação.
- **Login admin (WEB):** usuário `admin` / senha `desafio`.

## Regras de Cálculo (no backend)
- Pesos por dispositivo:
  - Celulares **0.8**, Computadores **0.5**, Smart TV **0.4**, TV Box **0.6**, Outros **0.1**.
- **Cliente Gamer**: multiplica o **peso total × 2**.
- Plano pela soma:
  - `< 1.0` → **Prata 100 Mb**
  - `1.0–2.0` (inclusive) → **Bronze 300 Mb**
  - `> 2.0 e < 3.0` → **Ouro 500 Mb**
  - `≥ 3.0` → **Diamante 800 Mb**

## Estrutura do Monorepo
