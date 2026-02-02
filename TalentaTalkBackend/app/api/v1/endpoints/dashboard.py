from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import (
    DashboardResponse, PaginatedListResponse, 
    AdminProfile, AdminUpdate, AdminPasswordUpdate
)
from app.schemas.response import ResponseBase
from app.api.deps import get_current_admin_user
from app.models.models import Manajemen
from app.utils.time_utils import TimeUtils
from typing import Optional
from datetime import datetime

router = APIRouter(dependencies=[Depends(get_current_admin_user)])

@router.get("/dashboard", response_model=ResponseBase[DashboardResponse])
async def get_dashboard(
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    activityLimit: int = Query(10, ge=1, le=200),
    daysBack: int = Query(30, ge=1),
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    
    start_dt = datetime.strptime(startDate, "%Y-%m-%d") if startDate else None
    end_dt = datetime.strptime(endDate, "%Y-%m-%d") if endDate else None
    
    data = await service.get_admin_dashboard(
        limit=activityLimit,
        days_back=daysBack,
        start_date=start_dt,
        end_date=end_dt
    )
    return ResponseBase(data=data, message="Dashboard data retrieved")

@router.get("/learners/top-active", response_model=ResponseBase[PaginatedListResponse])
async def get_top_active(
    searchQuery: str = Query(None), page: int = 1, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    data = await service.get_leaderboard("topActive", page, limit, searchQuery)
    return ResponseBase(data=data)

@router.get("/learners/highest-scoring", response_model=ResponseBase[PaginatedListResponse])
async def get_highest_scoring(
    category: str = Query("phoneme_material_exercise"), searchQuery: str = Query(None), page: int = 1, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    data = await service.get_leaderboard(category, page, limit, searchQuery)
    return ResponseBase(data=data)

@router.get("/profile", response_model=ResponseBase[AdminProfile])
async def get_profile(
    current_admin: Manajemen = Depends(get_current_admin_user)
):
    return ResponseBase(data=AdminProfile(
        idUser=f"ADM{current_admin.idmanajemen:03d}", 
        name=current_admin.namamanajemen, 
        email=current_admin.email, 
        role="Manajemen",
        createdAt="2025-01-01 00:00:00", 
        lastLogin=TimeUtils.format_to_wib(TimeUtils.get_current_time())
    ))

@router.put("/profile", response_model=ResponseBase)
async def update_profile(
    request: AdminUpdate, db: AsyncSession = Depends(get_db), current_admin: Manajemen = Depends(get_current_admin_user)
):
    service = DashboardService(db)
    await service.update_admin(current_admin.idmanajemen, request.nama, request.email)
    return ResponseBase(message="Profile updated successfully")

@router.put("/profile/change-password", response_model=ResponseBase)
async def change_password(
    request: AdminPasswordUpdate, db: AsyncSession = Depends(get_db), current_admin: Manajemen = Depends(get_current_admin_user)
):
    service = DashboardService(db)
    await service.change_admin_password(current_admin.idmanajemen, request.new_password)
    return ResponseBase(message="Password updated successfully")