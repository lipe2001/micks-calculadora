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
Aplicação completa (**frontend + backend**) para cálculo e contratação de planos de internet com base na quantidade de dispositivos.

## Stack
- **API (porta 3000):** FastAPI + SQLAlchemy + PostgreSQL
- **WEB (porta 3001):** FastAPI + Jinja2 + JavaScript
- **Banco:** PostgreSQL
- **E-mail dev:** MailHog
- **Orquestração:** Docker Compose

## Funcionalidades

## Logos da marca (PNG)
Coloque os arquivos em `apps/web/static/img/` com estes nomes:
- `micks-logo-blue.png` (logo principal azul para a calculadora)
- `micks-logo-white.png` (logo branca para telas escuras, usada no login)
- `micks-logo-symbol.png` (símbolo/ícone da marca, usado no painel de vendas)

### Frontend
- `GET /calculadora_plano`: formulário de dispositivos e opção de cliente gamer.
- Cálculo em tempo real no navegador chamando a API.
- Fluxo de contratação com nome, e-mail e telefone.
- `GET /login`: autenticação para o painel administrativo.
- `GET /vendas`: painel com listagem, filtro por cliente e ordenação por nome/data.

### Backend
- `POST /api/calculate`: cálculo do peso e recomendação de plano.
- `POST /api/contract`: registra venda no banco e envia e-mails para cliente e operações.
- `GET /api/sales`: lista vendas (protegido por Basic Auth admin/desafio).
- `GET /health`: health check.

## Regras de cálculo
Pesos por dispositivo:
- Celulares: **0.8**
- Computadores: **0.5**
- Smart TV: **0.4**
- TV Box: **0.6**
- Outros: **0.1**

Se `cliente gamer = true`, o peso total é multiplicado por `2`.

Plano por peso total:
- `< 1.0` → **Prata (100 Mb)**
- `>= 1.0 e <= 2.0` → **Bronze (300 Mb)**
- `> 2.0 e < 3.0` → **Ouro (500 Mb)**
- `>= 3.0` → **Diamante (800 Mb)**

## Como rodar com Docker Compose

```bash
cd infra
cp .env.example .env
docker compose up --build
```

Acessos:
- Calculadora: `http://localhost:3001/calculadora_plano`
- Painel de vendas: `http://localhost:3001/vendas`
- API docs: `http://localhost:3000/docs`
- MailHog: `http://localhost:8025`

## Credenciais
- Login WEB e Basic Auth API:
  - usuário: `admin`
  - senha: `desafio`

## Estrutura
```text
apps/
  api/
    main.py
  web/
    main.py
    templates/
    static/
infra/
  docker-compose.yml
  .env.example
```