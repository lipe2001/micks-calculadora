import uuid
from sqlalchemy import String, Integer, Boolean, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from ..core.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Dados do cliente
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    # Dispositivos
    n_cellphones: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_computers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_smart_tvs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_tv_box: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_others: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gamer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Resultado do cálculo
    total_weight: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    plan: Mapped[str] = mapped_column(String(20), nullable=False)
    speed_mbps: Mapped[int] = mapped_column(Integer, nullable=False)

    # Auditoria
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Sale {self.id} {self.email} {self.plan}/{self.speed_mbps}Mb>"