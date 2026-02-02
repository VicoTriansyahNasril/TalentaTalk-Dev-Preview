from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Manajemen
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login/talent")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Validasi Token untuk Talent (Mobile App)
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
            logger.warning(f"Talent Auth Failed: UserID={user_id}, Role={role}")
            raise credentials_exception
            
        return {"idtalent": user_id, "role": role}
        
    except JWTError as e:
        logger.error(f"JWT Error (Talent): {str(e)}")
        raise credentials_exception

async def get_current_admin_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Manajemen:
    """
    Validasi Token untuk Admin (Web Dashboard)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin credentials invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Decode Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        
        # 2. Validate Role
        if user_id is None:
            logger.warning("Admin Auth Failed: No User ID in token")
            raise credentials_exception
            
        # Allow both 'manajemen' and 'admin' roles for flexibility
        if role not in ["manajemen", "admin"]:
            logger.warning(f"Admin Auth Failed: Invalid Role '{role}' for user {user_id}")
            raise credentials_exception
            
        # 3. Check Database
        query = select(Manajemen).where(Manajemen.idmanajemen == user_id)
        result = await db.execute(query)
        admin = result.scalar_one_or_none()
        
        if admin is None:
            logger.warning(f"Admin Auth Failed: User ID {user_id} not found in DB")
            raise credentials_exception
            
        return admin
        
    except JWTError as e:
        logger.error(f"JWT Error (Admin): {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Auth Unexpected Error: {str(e)}")
        raise credentials_exception