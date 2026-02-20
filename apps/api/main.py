from fastapi import FastAPI
import os
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(40), nullable=False)
    devices: Mapped[dict] = mapped_column(JSON, nullable=False)
    gamer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    device_weights: Mapped[dict] = mapped_column(JSON, nullable=False)
    total_weight: Mapped[float] = mapped_column(Float, nullable=False)
    plan_name: Mapped[str] = mapped_column(String(50), nullable=False)
    plan_speed: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sales.db")
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Micks Calculadora API")
security = HTTPBasic()

DEVICE_WEIGHTS = {
    "cellphones": 0.8,
    "computers": 0.5,
    "smart_tvs": 0.4,
    "tv_boxes": 0.6,
    "others": 0.1,
}

PLANS = [
    ("Prata", "100 Mb", lambda w: w < 1.0),
    ("Bronze", "300 Mb", lambda w: 1.0 <= w <= 2.0),
    ("Ouro", "500 Mb", lambda w: 2.0 < w < 3.0),
    ("Diamante", "800 Mb", lambda w: w >= 3.0),
]


class DeviceInput(BaseModel):
    cellphones: int = Field(0, ge=0)
    computers: int = Field(0, ge=0)
    smart_tvs: int = Field(0, ge=0)
    tv_boxes: int = Field(0, ge=0)
    others: int = Field(0, ge=0)
    gamer: bool = False


class PlanResult(BaseModel):
    device_weights: dict[str, float]
    total_weight: float
    plan_name: Literal["Prata", "Bronze", "Ouro", "Diamante"]
    plan_speed: str


class ContractInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=40)
    devices: DeviceInput


class SaleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str
    devices: dict
    gamer: bool
    device_weights: dict
    total_weight: float
    plan_name: str
    plan_speed: str
    created_at: datetime


class ContractResponse(BaseModel):
    message: str
    sale: SaleResponse


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_plan(devices: DeviceInput) -> PlanResult:
    weighted = {
        key: round(getattr(devices, key) * weight, 2)
        for key, weight in DEVICE_WEIGHTS.items()
    }
    total_weight = round(sum(weighted.values()), 2)
    if devices.gamer:
        total_weight = round(total_weight * 2, 2)

    plan_name = "Diamante"
    plan_speed = "800 Mb"
    for name, speed, rule in PLANS:
        if rule(total_weight):
            plan_name = name
            plan_speed = speed
            break

    return PlanResult(
        device_weights=weighted,
        total_weight=total_weight,
        plan_name=plan_name,
        plan_speed=plan_speed,
    )


def send_email(to_email: str, subject: str, body: str) -> None:
    host = os.getenv("MAILHOG_SMTP_HOST", "mail")
    port = int(os.getenv("MAILHOG_SMTP_PORT", "1025"))
    sender = os.getenv("SMTP_FROM", "noreply@micks.com.br")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    with smtplib.SMTP(host, port, timeout=5) as smtp:
        smtp.sendmail(sender, [to_email], msg.as_string())


def build_contract_email(name: str, phone: str, devices: DeviceInput, result: PlanResult) -> str:
    return (
        f"Cliente: {name}\n"
        f"Telefone: {phone}\n"
        f"Celulares: {devices.cellphones}\n"
        f"Computadores: {devices.computers}\n"
        f"Smart TVs: {devices.smart_tvs}\n"
        f"TV Box: {devices.tv_boxes}\n"
        f"Outros: {devices.others}\n"
        f"Cliente gamer: {'Sim' if devices.gamer else 'Não'}\n"
        f"Pesos individuais: {result.device_weights}\n"
        f"Peso total: {result.total_weight}\n"
        f"Plano sugerido: {result.plan_name} - {result.plan_speed}\n"
    )


def require_admin(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    correct_user = os.getenv("ADMIN_USER", "admin")
    correct_pass = os.getenv("ADMIN_PASSWORD", "desafio")
    if credentials.username != correct_user or credentials.password != correct_pass:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "api",
        "database_url_present": bool(os.getenv("DATABASE_URL")),
        "mailhog": {
            "host": os.getenv("MAILHOG_SMTP_HOST", "mail"),
            "port": int(os.getenv("MAILHOG_SMTP_PORT", "1025")),
        },
    }


@app.post("/api/calculate", response_model=PlanResult)
def api_calculate(payload: DeviceInput):
    return calculate_plan(payload)


@app.post("/api/contract", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def api_contract(payload: ContractInput, db: Session = Depends(get_db)):
    result = calculate_plan(payload.devices)
    now = datetime.now(timezone.utc)

    sale = Sale(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        devices=payload.devices.model_dump(exclude={"gamer"}),
        gamer=payload.devices.gamer,
        device_weights=result.device_weights,
        total_weight=result.total_weight,
        plan_name=result.plan_name,
        plan_speed=result.plan_speed,
        created_at=now,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)

    email_body = build_contract_email(payload.name, payload.phone, payload.devices, result)
    ops_email = os.getenv("OPERATIONS_EMAIL", "operacoes@micks.com.br")

    try:
        send_email(payload.email, "Confirmação da contratação - Micks", email_body)
        send_email(ops_email, f"Nova venda - {payload.name}", email_body)
    except OSError:
        # Não impede a venda quando SMTP estiver indisponível em desenvolvimento.
        pass

    return ContractResponse(message="Contratação registrada com sucesso", sale=sale)


@app.get("/api/sales", response_model=list[SaleResponse], dependencies=[Depends(require_admin)])
def api_sales(
    db: Session = Depends(get_db),
    name: str | None = Query(default=None),
    sort_by: Literal["date", "name"] = Query(default="date"),
):
    query = select(Sale)

    if name:
        query = query.where(Sale.name.ilike(f"%{name}%"))

    if sort_by == "name":
        query = query.order_by(Sale.name.asc(), Sale.created_at.desc())
    else:
        query = query.order_by(Sale.created_at.desc())

    return list(db.scalars(query).all())