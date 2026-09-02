from pydantic import BaseModel, ConfigDict
from typing import Optional


class order(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customer_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    table_no: Optional[str] = None
    total: float
    status: str = "Pending"
    payment_id: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    amount_paid: Optional[float] = None