from pydantic import BaseModel, ConfigDict
from typing import Optional


class accounting(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    day: str
    revenue: float
    expenses: float
    orders: int = 0
