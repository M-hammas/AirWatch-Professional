from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class AlertIn(BaseModel):
    pollutant_code: str
    threshold: float = Field(gt=0)
    enabled: bool = True

class AlertOut(BaseModel):
    id: int
    pollutant_code: str
    threshold: float
    enabled: int
    class Config:
        from_attributes = True
