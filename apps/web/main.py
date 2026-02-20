import os
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Micks Calculadora WEB")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:3000")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "desafio")
AUTH_COOKIE = "micks_admin"


def is_logged(request: Request) -> bool:
    return request.cookies.get(AUTH_COOKIE) == "1"


@app.get("/health")
def health():
    return {"status": "ok", "service": "web", "api_base_url": API_BASE_URL}


@app.get("/")
def root_redirect():
    return RedirectResponse(url="/calculadora_plano", status_code=status.HTTP_302_FOUND)


@app.get("/calculadora_plano", response_class=HTMLResponse)
def calculator_page(request: Request):
    return templates.TemplateResponse(request, "calculator.html", {})


@app.post("/calculadora_plano/calculate")
async def calculator_result(request: Request):
    payload = await request.json()
    with httpx.Client(timeout=5.0) as client:
        response = client.post(f"{API_BASE_URL}/api/calculate", json=payload)
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/calculadora_plano/contract")
async def contract_plan(request: Request):
    payload = await request.json()
    with httpx.Client(timeout=8.0) as client:
        response = client.post(f"{API_BASE_URL}/api/contract", json=payload)

    if response.status_code >= 400:
        return JSONResponse({"ok": False, "message": response.text}, status_code=response.status_code)
    return JSONResponse({"ok": True, "message": "Contratação registrada com sucesso!"})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/login")
async def login_submit(request: Request):
    body = await request.json()
    if body.get("username") == ADMIN_USER and body.get("password") == ADMIN_PASSWORD:
        response = JSONResponse({"ok": True})
        response.set_cookie(AUTH_COOKIE, "1", httponly=True, samesite="lax")
        return response
    return JSONResponse({"ok": False, "message": "Usuário ou senha inválidos."}, status_code=401)


@app.post("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(AUTH_COOKIE)
    return response


@app.get("/vendas", response_class=HTMLResponse)
def sales_page(request: Request, name: str | None = None, sort_by: str = "date"):
    if not is_logged(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    params: dict[str, Any] = {"sort_by": sort_by}
    if name:
        params["name"] = name

    sales: list[dict[str, Any]] = []
    error: str | None = None

    with httpx.Client(timeout=8.0, auth=(ADMIN_USER, ADMIN_PASSWORD)) as client:
        response = client.get(f"{API_BASE_URL}/api/sales", params=params)
        if response.status_code < 400:
            sales = response.json()
        else:
            error = response.text

    return templates.TemplateResponse(
        request,
        "sales.html",
        {"sales": sales, "error": error, "name": name or "", "sort_by": sort_by},
    )
