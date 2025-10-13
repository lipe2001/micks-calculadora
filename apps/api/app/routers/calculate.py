from fastapi import APIRouter
from ..schemas import CalculateRequest, CalculateResponse

router = APIRouter(prefix="/api", tags=["calculate"])

# Pesos fixos (PDF)
W_CELL = 0.8
W_COMP = 0.5
W_SMART = 0.4
W_TVBOX = 0.6
W_OTHERS = 0.1

def classify_plan(total: float) -> tuple[str, int]:
    """
    Critérios do plano (PDF):
      < 1.0 → Prata 100 Mb
      1.0–2.0 (inclusive) → Bronze 300 Mb
      > 2.0 e < 3.0 → Ouro 500 Mb
      ≥ 3.0 → Diamante 800 Mb
    """
    if total < 1.0:
        return "Prata", 100
    if total <= 2.0:
        return "Bronze", 300
    if total < 3.0:
        return "Ouro", 500
    return "Diamante", 800

@router.post("/calculate", response_model=CalculateResponse)
def calculate(payload: CalculateRequest) -> CalculateResponse:
    total = (
        payload.n_cellphones * W_CELL +
        payload.n_computers * W_COMP +
        payload.n_smart_tvs * W_SMART +
        payload.n_tv_box * W_TVBOX +
        payload.n_others * W_OTHERS
    )
    if payload.gamer:
        total *= 2

    # Arredondamos para 2 casas para exibição consistente
    total = round(float(total), 2)

    plan, speed = classify_plan(total)
    return CalculateResponse(total_weight=total, plan=plan, speed_mbps=speed)
