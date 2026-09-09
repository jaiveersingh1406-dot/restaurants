from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class product(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    image: Optional[str] = None
    images: Optional[list] = None
    rating: float = Field(default=0, ge=0, le=5)
    status: str = Field(default="Available", pattern="^(Available|Unavailable|Low Stock)$")
    stock: int = 0