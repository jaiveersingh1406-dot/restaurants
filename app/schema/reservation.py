from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional


class reservation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customer_name: str
    guests: int = 2
    reservation_date: Optional[date] = None
    time_slot: str
    phone: Optional[str] = None
    table_no: str = "T-01"
    special_request: Optional[str] = None
    status: str = "Pending"
