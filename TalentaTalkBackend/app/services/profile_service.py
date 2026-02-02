from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.talent_repository import TalentRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.core.exceptions import NotFoundError
from app.utils.time_utils import TimeUtils
from sqlalchemy import select, func
from app.models.models import Materifonemkata, Materifonemkalimat

class ProfileService:
    def __init__(self, db: AsyncSession):
        self.talent_repo = TalentRepository(db)
        self.dash_repo = DashboardRepository(db)
        self.db = db

    async def get_mobile_profile(self, talent_id: int):
        # 1. Validasi Talent
        talent = await self.talent_repo.get_by_id(talent_id)
        if not talent:
            raise NotFoundError("Talent")
            
        # 2. Ambil Statistik Dasar (Exam)
        progress_stats = await self.talent_repo.get_talent_progress_stats(talent_id)
        
        # 3. Ambil Statistik Pronunciation (Avg Score & Count)
        avg_pronunciation = await self.dash_repo.get_user_avg_pronunciation(talent_id)
        pron_completed_count = await self.dash_repo.get_user_phoneme_counts(talent_id)
        
        # Hitung total materi phoneme yang tersedia (untuk progress bar)
        count_word = await self.db.scalar(select(func.count(Materifonemkata.idmaterifonemkata)))
        count_sent = await self.db.scalar(select(func.count(Materifonemkalimat.idmaterifonemkalimat)))
        total_phoneme_material = (count_word or 0) + (count_sent or 0)

        # 4. Ambil Statistik Conversation (WPM & Count)
        conv_stats = await self.dash_repo.get_user_conversation_stats(talent_id)
        
        # 5. Ambil Statistik Interview (WPM & Count)
        int_stats = await self.dash_repo.get_user_interview_stats(talent_id)
        
        # 6. Hitung Streak (Logic Penuh)
        activity_dates = await self.dash_repo.get_user_activity_dates(talent_id)
        highest_streak, current_streak = TimeUtils.calculate_streaks(activity_dates)
        
        return {
            "name": talent.nama,
            "jobTitle": talent.role,
            "email": talent.email,
            "pretestScore": talent.pretest_score or 0,
            
            # Exam Stats
            "highestExam": progress_stats['highest_exam'] or 0,
            "lastTest": progress_stats['latest_exam'] or 0,
            
            # Average Scores
            "averagePronunciation": round(avg_pronunciation, 2),
            "averageWPMConversation": round(conv_stats["avg_wpm"], 2),
            "averageWPMInterview": round(int_stats["avg_wpm"], 2),
            
            # Streaks
            "highestStreak": highest_streak,
            "currentStreak": current_streak,
            
            # Activity Counts
            "activity": {
                "phonemeCompleted": pron_completed_count,
                "phonemeTotal": total_phoneme_material,
                "conversationCompleted": conv_stats["count"],
                "interviewCompleted": int_stats["count"]
            }
        }