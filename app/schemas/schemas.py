from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# License schemas
class LicenseBase(BaseModel):
    expires_at: datetime
    allowed_ips: Optional[str] = None

class LicenseCreate(LicenseBase):
    pass

class License(LicenseBase):
    id: int
    key: str
    created_at: datetime
    is_active: bool
    owner_id: int

    class Config:
        orm_mode = True

# Activation schemas
class ActivationBase(BaseModel):
    ip_address: str
    machine_id: str

class ActivationCreate(ActivationBase):
    license_key: str

class Activation(ActivationBase):
    id: int
    license_id: int
    activated_at: datetime
    last_check_in: datetime

    class Config:
        orm_mode = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# License verification
class LicenseVerify(BaseModel):
    license_key: str
    machine_id: str
    ip_address: Optional[str] = None