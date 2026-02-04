from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.talent_service import TalentService
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.response import ResponseBase
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/summary", response_model=ResponseBase)
async def get_home_summary(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    talent_id = current_user["idtalent"]
    dash_repo = DashboardRepository(db)
    talent_service = TalentService(db)
    
    talent_detail = await talent_service.get_talent_detail(talent_id)
    phoneme_count = await dash_repo.get_user_phoneme_counts(talent_id)
    avg_pronunciation = await dash_repo.get_user_avg_pronunciation(talent_id)
    conv_stats = await dash_repo.get_user_conversation_stats(talent_id)
    int_stats = await dash_repo.get_user_interview_stats(talent_id)
    
    speaking_sessions = (conv_stats["count"] or 0) + (int_stats["count"] or 0)
    avg_wpm = ((conv_stats["avg_wpm"] or 0) + (int_stats["avg_wpm"] or 0)) / 2 if speaking_sessions > 0 else 0
    
    progress = await talent_service.repo.get_talent_progress_stats(talent_id)
    
    data = {
        "user": {
            "id": talent_id,
            "name": talent_detail["nama"]
        },
        "learning_streak": {
            "current_streak": 1,
            "this_week_activities": 0
        },
        "quick_stats": {
            "total_training_sessions": phoneme_count + speaking_sessions,
            "avg_phoneme_score": round(avg_pronunciation, 1),
            "avg_speaking_wpm": round(avg_wpm, 1),
            "phoneme_sessions": phoneme_count,
            "speaking_sessions": speaking_sessions
        },
        "recent_activities": {
            "total": 0,
            "data": [] 
        },
        "exam_summary": {
            "latest_exam_score": progress.get('latest_exam') or 0,
            "total_exams": 0,
            "average_exam_score": 0,
            "last_exam_days_ago": 0
        }
    }
    
    return ResponseBase(data=data)