# view/HomeView.py - CLEAN VERSION WITH FLEXIBLE ACTIVITY LIMITS
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from controller.AuthController import get_current_admin_user
from controller.HomeController import HomeController
from database import get_db
from utils.timestamp_helper import TimestampHelper
from schemas import ChangePasswordRequest, UpdateAdminProfileRequest
from models import Manajemen
from utils.response_formatter import APIResponse

homerouter = APIRouter(
    prefix="/web/admin",
    dependencies=[Depends(get_current_admin_user)]
)

# ================================
# DASHBOARD ENDPOINTS - ENHANCED WITH FLEXIBLE LIMITS
# ================================

@homerouter.get("/dashboard")
def admin_dashboard(
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    activityLimit: int = Query(10, ge=1, le=200, description="Number of activities to show (1-200)"),
    daysBack: int = Query(30, ge=1, le=90, description="Days to look back (1-90)"),
    db: Session = Depends(get_db)
):
    """Enhanced Admin Dashboard with Configurable Activity Limits"""
    try:
        controller = HomeController(db)
        
        # Get basic dashboard stats
        dashboard_stats = controller.get_dashboard_stats()
        
        # Get enhanced activities with configurable limits
        recent_activities_result = controller.get_recent_activities(
            limit=activityLimit, 
            days_back=daysBack
        )
        
        # Enhanced response data with limit information
        response_data = {
            "statistics": {
                "totalTalent": dashboard_stats.get("statistics", {}).get("totalTalent", 0),
                "totalPronunciationMaterial": dashboard_stats.get("statistics", {}).get("totalPronunciationMaterial", 0),
                "totalExamPhonemMaterial": dashboard_stats.get("statistics", {}).get("totalExamPhonemMaterial", 0),
                "totalInterviewQuestion": dashboard_stats.get("statistics", {}).get("totalInterviewQuestion", 0)
            },
            "pronunciationActivities": recent_activities_result.get("pronunciationActivities", []),
            "speakingActivities": recent_activities_result.get("speakingActivities", []),
            "totalActivities": recent_activities_result.get("totalActivities", 0),
            "dateRange": recent_activities_result.get("dateRange", f"Last {daysBack} days"),
            "hasError": recent_activities_result.get("hasError", False),
            "activitySettings": {
                "requestedLimit": activityLimit,
                "actualPronunciationCount": recent_activities_result.get("pronunciationLimit", 0),
                "actualSpeakingCount": recent_activities_result.get("speakingLimit", 0),
                "daysBack": daysBack,
                "availableLimits": [10, 25, 50, 100],
                "maxLimit": 200,
                "minLimit": 1
            }
        }
        
        return APIResponse.success(
            data=response_data,
            message=f"Enhanced dashboard data with {activityLimit} activities per category ({daysBack} days back) berhasil diambil"
        )
        
    except Exception as e:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@homerouter.get("/dashboard/pronunciation-activities") 
def get_pronunciation_activities(
    limit: int = Query(10, ge=1, le=200, description="Number of activities to show"),
    daysBack: int = Query(30, ge=1, le=90, description="Days to look back"),
    db: Session = Depends(get_db)
):
    """Get pronunciation activities with configurable limits"""
    try:
        controller = HomeController(db)
        result = controller.get_recent_pronunciation_activities(limit, daysBack)
        
        return APIResponse.success(
            data=result,
            message=f"Pronunciation activities (limit: {limit}, days: {daysBack}) berhasil diambil"
        )
        
    except Exception as e:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@homerouter.get("/dashboard/speaking-activities")
def get_speaking_activities(
    limit: int = Query(10, ge=1, le=200, description="Number of activities to show"),
    daysBack: int = Query(30, ge=1, le=90, description="Days to look back"),
    db: Session = Depends(get_db)
):
    """Get speaking activities with configurable limits"""
    try:
        controller = HomeController(db)
        result = controller.get_recent_speaking_activities(limit, daysBack)
        
        return APIResponse.success(
            data=result,
            message=f"Speaking activities (limit: {limit}, days: {daysBack}) berhasil diambil"
        )
        
    except Exception as e:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ================================
# LEARNERS MANAGEMENT - UNCHANGED
# ================================

@homerouter.get("/learners/top-active")
def get_top_active_learners(
    searchQuery: Optional[str] = Query(None, alias="searchQuery"),
    page: int = Query(1, ge=1),
    limit: int = Query(10),
    sortBy: Optional[str] = Query(None),
    sortOrder: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Top Active Learners"""
    try:
        controller = HomeController(db)
        result = controller.get_top_active_learners(searchQuery, page, limit)
        
        if not result.get("data") or not result["data"].get("learners"):
            response_data = {
                "learners": [],
                "pagination": {
                    "currentPage": page,
                    "totalPages": 0,
                    "totalRecords": 0,
                    "showing": "0 records found"
                }
            }
            return APIResponse.success(
                data=response_data,
                message="Data tidak ditemukan"
            )
        
        return APIResponse.success(
            data=result["data"],
            message=result.get("message", "Data learner aktif berhasil diambil")
        )
        
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@homerouter.get("/learners/highest-scoring")
def get_highest_scoring_learners(
    category: Optional[str] = Query("phoneme_material_exercise"),
    searchQuery: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10),
    sortBy: Optional[str] = Query(None),
    sortOrder: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Highest Scoring Learners untuk berbagai kategori"""
    try:
        controller = HomeController(db)
        
        valid_categories = ["phoneme_material_exercise", "phoneme_exercise", "phoneme_exam", "conversation", "interview"]
        if category not in valid_categories:
            return APIResponse.error(
                message="Kategori tidak valid",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if category == "phoneme_material_exercise":
            result = controller.get_highest_scoring_learners_phoneme_material(searchQuery, page, limit)
        elif category == "phoneme_exercise":
            result = controller.get_highest_scoring_learners_phoneme_exercise(searchQuery, page, limit)
        elif category == "phoneme_exam":
            result = controller.get_highest_scoring_learners_phoneme_exam(searchQuery, page, limit)
        elif category == "conversation":
            result = controller.get_conversation_results(searchQuery, page, limit)
        elif category == "interview":
            result = controller.get_interview_results(searchQuery, page, limit)
        
        if not result.get("data") or not result["data"].get("learners"):
            response_data = {
                "learners": [],
                "pagination": {
                    "currentPage": page,
                    "totalPages": 0,
                    "totalRecords": 0,
                    "showing": "No data available"
                },
                "categoryInfo": {
                    "activeTab": category,
                    "availableTabs": valid_categories
                }
            }
            return APIResponse.success(
                data=response_data,
                message="Belum ada data untuk kategori ini"
            )
        
        return APIResponse.success(
            data=result["data"],
            message=result.get("message", "Data ranking berhasil diambil")
        )
        
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ================================
# ADMIN PROFILE MANAGEMENT - UNCHANGED
# ================================

@homerouter.get("/profile")
def get_admin_profile(
    db: Session = Depends(get_db),
    current_admin: Manajemen = Depends(get_current_admin_user)
):
    """Get admin profile"""
    try:
        response_data = {
            "adminId": f"ADM{current_admin.idmanajemen:03d}",
            "fullName": current_admin.namamanajemen,
            "email": current_admin.email,
            "role": "Manajemen",
            "createdAt": current_admin.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(current_admin, 'created_at') and current_admin.created_at else "2025-01-15 08:00:00",
            "lastLogin": TimestampHelper.get_current_timestamp() 
        }
        
        return APIResponse.success(
            data=response_data,
            message="Profile admin berhasil diambil"
        )
        
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@homerouter.put("/profile")
def update_admin_profile(
    request: UpdateAdminProfileRequest,
    db: Session = Depends(get_db),
    current_admin: Manajemen = Depends(get_current_admin_user)
):
    """Update admin profile"""
    try:
        controller = HomeController(db)
        
        existing_admin = db.query(Manajemen).filter(
            Manajemen.email == request.email,
            Manajemen.idmanajemen != current_admin.idmanajemen
        ).first()
        
        if existing_admin:
            return APIResponse.error(
                message="Email sudah digunakan oleh admin lain",
                status_code=status.HTTP_409_CONFLICT
            )
        
        result = controller.update_admin_profile(current_admin.idmanajemen, request.nama, request.email)
        
        response_data = {
            "adminId": f"ADM{current_admin.idmanajemen:03d}",
            "fullName": request.nama,
            "email": request.email,
            "role": "Manajemen",
            "updatedAt": TimestampHelper.get_current_timestamp()
        }
        
        return APIResponse.success(
            data=response_data,
            message="Profile admin berhasil diperbarui"
        )
        
    except HTTPException as e:
        if "validation" in str(e.detail).lower():
            return APIResponse.error(
                message=str(e.detail),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        raise e
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@homerouter.put("/profile/change-password")
def change_admin_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_admin: Manajemen = Depends(get_current_admin_user)
):
    """Change admin password"""
    try:
        if not request.new_password:
            return APIResponse.error(
                message="New password tidak boleh kosong",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        controller = HomeController(db)
        result = controller.change_admin_password(current_admin.idmanajemen, request.new_password)
        
        response_data = {
            "adminId": f"ADM{current_admin.idmanajemen:03d}",
            "updatedAt": TimestampHelper.get_current_timestamp()
        }
        
        return APIResponse.success(
            data=response_data,
            message="Password berhasil diperbarui"
        )
        
    except HTTPException as e:
        if "validation" in str(e.detail).lower() or "Password minimal" in str(e.detail):
            return APIResponse.error(
                message=str(e.detail),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        raise e
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )