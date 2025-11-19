# controller/AuthController.py
from fastapi import HTTPException, status, Depends, Header
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database import get_db
from models import Talent, Manajemen
from dotenv import load_dotenv
from schemas import LoginRequest, LoginResponse, CreateTalentRequest, TokenResponse
import bcrypt
import os
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

# Konfigurasi JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/talent")

def hash_password(password: str):
    """Hash password menggunakan bcrypt"""
    return pwd_context.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password dengan stored hash"""
    try:
        password_bytes = password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, stored_hash.encode('utf-8'))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Membuat JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ================================
# WEB APPLICATION AUTH (MANAJEMEN)
# ================================

def login_manajemen(request: LoginRequest, db: Session) -> dict:
    """Login untuk manajemen/admin - Web Application"""
    try:
        user = db.query(Manajemen).filter(Manajemen.email == request.email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        if not verify_password(request.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token_data = {
            "sub": user.email,
            "role": "manajemen",
            "id": user.idmanajemen
        }
        token = create_access_token(token_data)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": "manajemen",
            "id": user.idmanajemen,
            "name": user.namamanajemen,
            "email": user.email
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

def login_talent(request: LoginRequest, db: Session) -> TokenResponse:
    """Login untuk talent - Mobile Application"""
    try:
        user = db.query(Talent).filter(Talent.email == request.email).first()
        if not user or not verify_password(request.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token_data = {
            "sub": user.email,
            "role": "talent",
            "id": user.idtalent
        }
        token = create_access_token(token_data)
        return TokenResponse(access_token=token, token_type="bearer", role="talent")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

def create_talent(request: CreateTalentRequest, db: Session) -> dict:
    """Pendaftaran Talent oleh Manajemen"""
    try:
        existing = db.query(Talent).filter(Talent.email == request.email).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email sudah digunakan")

        hashed_password = hash_password(request.password)
        new_talent = Talent(
            email=request.email,
            password=hashed_password,
            nama=request.nama
        )
        db.add(new_talent)
        db.commit()
        db.refresh(new_talent)
        return {
            "id": new_talent.idtalent,
            "email": new_talent.email,
            "nama": new_talent.nama,
            "password": new_talent.password
        }
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

def get_current_user(authorization: str = Header(None)):
    """Get current talent user dari token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        
        if user_id is None or role != "talent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token payload",
            )
        return {"idtalent": user_id}
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate token: {str(e)}",
        )

def get_current_admin_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> Manajemen:
    """Get current admin user untuk Web Application"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token tidak valid",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        exp: int = payload.get("exp")
        
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session telah berakhir, silakan login kembali"
            )
        
        if user_id is None or role != "manajemen":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token tidak valid",
            )
        
        admin = db.query(Manajemen).filter(Manajemen.idmanajemen == user_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token tidak valid"
            )
        
        return admin
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
        )