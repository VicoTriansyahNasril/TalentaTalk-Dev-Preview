from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.exceptions import AuthenticationError, DuplicateError
from app.repositories.talent_repository import TalentRepository
from app.schemas.auth import LoginRequest, TalentCreate
from app.models.models import Manajemen
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, talent_repo: TalentRepository):
        self.talent_repo = talent_repo

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, subject: Union[str, Any], role: str, extra_data: dict = None) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "exp": expire, 
            "sub": str(subject), 
            "role": role, 
            "id": subject
        }
        if extra_data:
            to_encode.update(extra_data)
            
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def authenticate_talent(self, login_data: LoginRequest) -> dict:
        talent = await self.talent_repo.get_by_email(login_data.email)
        
        if not talent:
            raise AuthenticationError("Email tidak terdaftar")
        
        if not self.verify_password(login_data.password, talent.password):
            raise AuthenticationError("Password salah")
        
        token = self.create_access_token(talent.idtalent, role="talent")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": "talent",
            "user_id": str(talent.idtalent)
        }

    async def register_talent(self, data: TalentCreate):
        existing = await self.talent_repo.get_by_email(data.email)
        if existing:
            raise DuplicateError("Email sudah terdaftar")
        
        hashed_pw = self.get_password_hash(data.password)
        
        new_talent_data = {
            "nama": data.nama,
            "email": data.email,
            "password": hashed_pw,
            "role": data.role
        }
        
        return await self.talent_repo.create(new_talent_data)
    
    async def authenticate_admin(self, login_data: LoginRequest, db_session: AsyncSession) -> dict:
        """Autentikasi khusus untuk Manajemen/Admin"""
        query = select(Manajemen).where(Manajemen.email == login_data.email)
        result = await db_session.execute(query)
        admin = result.scalar_one_or_none()
        
        if not admin:
            raise AuthenticationError("Admin email tidak terdaftar")
        
        if not self.verify_password(login_data.password, admin.password):
            raise AuthenticationError("Password admin salah")
            
        token = self.create_access_token(admin.idmanajemen, role="manajemen")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "idUser": f"ADM{admin.idmanajemen:03d}",
            "name": admin.namamanajemen,
            "role": "admin",
            "email": admin.email
        }