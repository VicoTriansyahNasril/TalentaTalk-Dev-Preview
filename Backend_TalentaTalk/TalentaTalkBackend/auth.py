# auth.py
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Manajemen
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Konfigurasi
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # tidak dipakai langsung tapi diperlukan

# Ambil koneksi DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Buat token akses
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verifikasi token dan ambil user manajemen
def get_current_manajemen(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Manajemen:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if user_id is None or role != "manajemen":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Manajemen).filter_by(idmanajemen=user_id).first()
    if user is None:
        raise credentials_exception
    return user
