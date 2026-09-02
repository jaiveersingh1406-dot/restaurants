from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class product(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    image: Optional[str] = None
    status: str = Field(default="Available", pattern="^(Available|Unavailable)$")
    stock: int = 0
    
    