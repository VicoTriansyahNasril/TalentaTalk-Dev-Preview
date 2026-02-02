from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TalentCreate(BaseModel):
    nama: str
    email: EmailStr
    password: str
    role: str = "talent"

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int