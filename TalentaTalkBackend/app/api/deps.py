from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.repositories.talent_repository import TalentRepository
from app.models.models import Manajemen
from sqlalchemy import select

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login/talent")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Validasi Token untuk Talent (Mobile App)
    Mengembalikan dict user info sederhana.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        
        if user_id is None or role != "talent":
            raise credentials_exception
            
        return {"idtalent": user_id, "role": role}
        
    except JWTError:
        raise credentials_exception

async def get_current_admin_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Manajemen:
    """
    Validasi Token untuk Admin (Web Dashboard)
    Mengembalikan objek Manajemen lengkap.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin credentials invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if user_id is None or role not in ["manajemen", "admin"]:
            raise credentials_exception
            
        query = select(Manajemen).where(Manajemen.idmanajemen == user_id)
        result = await db.execute(query)
        admin = result.scalar_one_or_none()
        
        if admin is None:
            raise credentials_exception
            
        return admin
        
    except JWTError:
        raise credentials_exception