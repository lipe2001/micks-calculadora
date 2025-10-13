from fastapi import FastAPI
from .routers import health
from .routers import calculate

app = FastAPI(title="Micks Calculadora API")

# Rotas
app.include_router(health.router)
app.include_router(calculate.router)
