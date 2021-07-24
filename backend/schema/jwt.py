from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class _JWTUser(BaseModel):
    id: str
    rollno: int


class JWTToken(BaseModel):
    exp: Optional[datetime]
    sub: Optional[_JWTUser]
