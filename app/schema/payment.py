from pydantic import BaseModel, ConfigDict
from typing import Optional


class payment_init(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    amount: float
    receipt: Optional[str] = None


class payment_verify(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    razorpay_order_id: str
    payment_id: str
    signature: str
    customer_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    table_no: Optional[str] = None
    total: float
    payment_method: Optional[str] = None