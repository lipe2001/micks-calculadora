from fastapi import FastAPI
import io
import os
import zipfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

import httpx
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
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

DEVICE_LABELS = {
    "cellphones": "Celulares",
    "computers": "Computadores",
    "smart_tvs": "Smart TVs",
    "tv_boxes": "TV Box",
    "others": "Outros",
}


def is_logged(request: Request) -> bool:
    return request.cookies.get(AUTH_COOKIE) == "1"


def fetch_sales(name: str | None = None, sort_by: str = "date") -> tuple[list[dict[str, Any]], str | None]:
    params: dict[str, Any] = {"sort_by": sort_by}
    if name:
        params["name"] = name

    try:
        with httpx.Client(timeout=8.0, auth=(ADMIN_USER, ADMIN_PASSWORD)) as client:
            response = client.get(f"{API_BASE_URL}/api/sales", params=params)
            if response.status_code < 400:
                return response.json(), None
            return [], response.text
    except httpx.RequestError as exc:
        return [], str(exc)


def _excel_cell(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"<c t=\"n\"><v>{value}</v></c>"
    text = escape(str(value or ""))
    return f"<c t=\"inlineStr\"><is><t>{text}</t></is></c>"


def build_xlsx(rows: list[list[Any]]) -> bytes:
    sheet_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = "".join(_excel_cell(cell) for cell in row)
        sheet_rows.append(f"<row r=\"{row_index}\">{cells}</row>")

    sheet_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"
        "<sheetData>"
        + "".join(sheet_rows)
        + "</sheetData></worksheet>"
    )

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

    workbook = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Vendas" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>"""

    workbook_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    return buffer.getvalue()


@app.get("/health")
def health():
    return {"status": "ok", "service": "web"}
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

    sales, error = fetch_sales(name=name, sort_by=sort_by)

    return templates.TemplateResponse(
        request,
        "sales.html",
        {
            "sales": sales,
            "error": error,
            "name": name or "",
            "sort_by": sort_by,
            "device_labels": DEVICE_LABELS,
        },
    )


@app.get("/vendas/export.xlsx")
def export_sales(request: Request, name: str | None = None, sort_by: str = "date"):
    if not is_logged(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    sales, error = fetch_sales(name=name, sort_by=sort_by)
    if error:
        return JSONResponse({"detail": f"Erro ao exportar vendas: {error}"}, status_code=502)

    rows: list[list[Any]] = [
        [
            "Data",
            "Nome",
            "E-mail",
            "Telefone",
            "Celulares",
            "Computadores",
            "Smart TVs",
            "TV Box",
            "Outros",
            "Peso total",
            "Plano",
            "Velocidade",
        ]
    ]

    for sale in sales:
        devices = sale.get("devices", {})
        rows.append(
            [
                sale.get("created_at", ""),
                sale.get("name", ""),
                sale.get("email", ""),
                sale.get("phone", ""),
                devices.get("cellphones", 0),
                devices.get("computers", 0),
                devices.get("smart_tvs", 0),
                devices.get("tv_boxes", 0),
                devices.get("others", 0),
                sale.get("total_weight", 0),
                sale.get("plan_name", ""),
                sale.get("plan_speed", ""),
            ]
        )

    content = build_xlsx(rows)
    filename = "vendas_micks.xlsx"
    headers_response = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers_response,
    )