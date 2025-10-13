from pydantic import BaseModel, Field, conint

class CalculateRequest(BaseModel):
    n_cellphones: conint(ge=0) = Field(0, description="Quantidade de celulares")
    n_computers: conint(ge=0) = Field(0, description="Quantidade de computadores")
    n_smart_tvs: conint(ge=0) = Field(0, description="Quantidade de Smart TVs")
    n_tv_box: conint(ge=0) = Field(0, description="Quantidade de TV Box")
    n_others: conint(ge=0) = Field(0, description="Outros dispositivos")
    gamer: bool = Field(False, description="Cliente Gamer multiplica o peso total por 2")

class CalculateResponse(BaseModel):
    total_weight: float
    plan: str
    speed_mbps: int
