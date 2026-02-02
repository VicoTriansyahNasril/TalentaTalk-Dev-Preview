from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.talent_repository import TalentRepository
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, TalentCreate
from app.schemas.response import ResponseBase

router = APIRouter()

@router.post("/login", response_model=ResponseBase) 
async def login_admin(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    repo = TalentRepository(db) 
    service = AuthService(repo)
    result = await service.authenticate_admin(request, db)
    return ResponseBase(data=result, message="Admin login successful")

# Endpoint Talent (Mobile)
@router.post("/login/talent", response_model=ResponseBase)
async def login_talent(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    repo = TalentRepository(db)
    service = AuthService(repo)
    result = await service.authenticate_talent(request)
    return ResponseBase(data=result, message="Login successful")

@router.post("/register/talent", response_model=ResponseBase, status_code=status.HTTP_201_CREATED)
async def register_talent(
    request: TalentCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = TalentRepository(db)
    service = AuthService(repo)
    result = await service.register_talent(request)
    return ResponseBase(message="Talent created successfully", data={"email": result.email})