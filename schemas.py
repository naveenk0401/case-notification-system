from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# ------------------ USER SCHEMAS ------------------
class UserBase(BaseModel):
    name: str
    username: str
    email: EmailStr
    mobile: str


class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):   
    username: str
    password: str

class UserResponse(UserBase):
    id: int

class Config:
    from_attributes = True

class UserOut(BaseModel):
    id: int
    name: str
    username: str
    email: str
    mobile: str
    is_admin: bool 

class Config:
    from_attributes = True


# ------------------ LOGIN SCHEMA ------------------
class LoginRequest(BaseModel):
    username: str
    password: str


# ------------------ TOKEN SCHEMA ------------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ------------------ CASE SCHEMAS ------------------
class CaseBase(BaseModel):
    case_details: str
    status: str
    next_hearing_date: date


class CaseCreate(CaseBase):
    user_id: int
class CaseOut(BaseModel):
    case_id: int
    case_details: str
    status: str
    next_hearing_date: date
    created_at: date

class Config:
    from_attributes = True


class CaseResponse(CaseBase):
    case_id: int
    user_id: int

class Config:
    from_attributes = True

