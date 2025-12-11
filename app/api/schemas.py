# app/api/schemas.py
from pydantic import BaseModel, EmailStr

# Request: Signup/Login
class UserCreate(BaseModel):
    fullname: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response: public user data (no password)
class UserResponse(BaseModel):
    id: int
    fullname: str
    email: EmailStr

    class Config:
        orm_mode = True

# Response: login response → token + user
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
