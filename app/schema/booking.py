from pydantic import BaseModel
from datetime import date, time
from typing import Optional


class BookingCreate(BaseModel):
    user_id: int
    booking_date: date
    booking_time: time
    guests: int
    table_number: Optional[int] = None
    special_request: Optional[str] = None


class BookingResponse(BaseModel):
    id: int
    user_id: int
    booking_date: date
    booking_time: time
    guests: int
    table_number: Optional[int] = None
    status: str
    special_request: Optional[str] = None

    class Config:
        from_attributes = True


class BookingStatusUpdate(BaseModel):
    status: str
    