# view/AuthView.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from controller.AuthController import login_manajemen, login_talent, create_talent
from schemas import LoginRequest, LoginResponse, CreateTalentRequest
from database import get_db
from utils.response_formatter import APIResponse

authrouter = APIRouter()

# POST /web/admin/login - Login endpoint untuk admin web application
@authrouter.post("/web/admin/login")
def login_manajemen_web(request: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint untuk manajemen/admin - Web Application"""
    try:
        if not request.email or not request.password:
            return APIResponse.error(
                message="Email dan password wajib diisi",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        result = login_manajemen(request, db)
        from models import Manajemen
        admin = db.query(Manajemen).filter(Manajemen.email == request.email).first()
        response_data = {
            "token": result["access_token"],
            "idUser": f"ADM{admin.idmanajemen:03d}",
            "name": admin.namamanajemen,
            "role": "admin",
            "email": admin.email
        }
        
        return APIResponse.success(
            data=response_data,
            message="Login berhasil",
            status_code=status.HTTP_200_OK
        )
        
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            from models import Manajemen
            admin_exists = db.query(Manajemen).filter(Manajemen.email == request.email).first()
            if not admin_exists:
                return APIResponse.error(
                    message="Email tidak terdaftar",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            else:
                return APIResponse.error(
                    message="Password salah", 
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
        return APIResponse.error(
            message=e.detail,
            status_code=e.status_code
        )
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan pada server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# POST /login/talent - Login endpoint untuk talent mobile application
@authrouter.post("/login/talent", response_model=LoginResponse)
def login_talent_view(request: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint untuk talent - Mobile Application"""
    return login_talent(request, db)

# POST /create/talent - Create talent endpoint untuk manajemen
@authrouter.post("/create/talent", response_model=CreateTalentRequest)
def create_talent_view(request: CreateTalentRequest, db: Session = Depends(get_db)):
    """Create talent endpoint untuk manajemen"""
    return create_talent(request, db)