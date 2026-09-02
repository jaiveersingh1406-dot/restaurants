from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class signup(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str = Field(..., alias="name")
    email: str
    password: str


class login(BaseModel):
    email: str = Field(..., pattern=r"^\S+@\S+\.\S+$")
    password: str = Field(..., min_length=6)
    role: Optional[str] = Field(default=None, pattern=r"^(admin|user)$")


class change_password(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class profile_update(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    phone: Optional[str] = None
