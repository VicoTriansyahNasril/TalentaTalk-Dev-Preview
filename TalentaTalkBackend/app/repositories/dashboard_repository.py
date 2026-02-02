from sqlalchemy import select, func, desc, union_all, literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import (
    Talent, Materifonemkata, Materifonemkalimat, Materiujian, Materiinterview,
    Hasillatihanfonem, Hasillatihanpercakapan, Hasillatihaninterview, Ujianfonem, Manajemen
)
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_counts(self) -> Dict[str, int]:
        total_talent = await self.db.scalar(select(func.count(Talent.idtalent)))
        count_word = await self.db.scalar(select(func.count(Materifonemkata.idmaterifonemkata)))
        count_sent = await self.db.scalar(select(func.count(Materifonemkalimat.idmaterifonemkalimat)))
        total_exam = await self.db.scalar(select(func.count(func.distinct(Materiujian.kategori))))
        total_interview = await self.db.scalar(select(func.count(Materiinterview.idmateriinterview)))
        
        return {
            "totalTalent": total_talent or 0,
            "totalPronunciationMaterial": (count_word or 0) + (count_sent or 0),
            "totalExamPhonemMaterial": total_exam or 0,
            "totalInterviewQuestion": total_interview or 0
        }

    async def get_recent_activities(
        self, 
        limit: int = 10, 
        days_back: int = 30,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        
        # Calculate Date Range
        if start_date and end_date:
            cutoff_start = start_date
            cutoff_end = end_date
        else:
            cutoff_start = datetime.utcnow() - timedelta(days=days_back)
            cutoff_end = datetime.utcnow() + timedelta(days=1) # Future buffer

        # Helper to apply date filter
        def date_filter(model_date_col):
            return model_date_col.between(cutoff_start, cutoff_end)

        q_phoneme = select(
            Hasillatihanfonem.idtalent, Hasillatihanfonem.nilai.label("score_val"),
            Hasillatihanfonem.waktulatihan, Hasillatihanfonem.typelatihan.label("category"),
            literal_column("'Phoneme'").label("type")
        ).where(date_filter(Hasillatihanfonem.waktulatihan))

        q_exam = select(
            Ujianfonem.idtalent, Ujianfonem.nilai.label("score_val"),
            Ujianfonem.waktuujian.label("waktulatihan"), Ujianfonem.kategori.label("category"),
            literal_column("'Exam'").label("type")
        ).where(date_filter(Ujianfonem.waktuujian))

        q_conv = select(
            Hasillatihanpercakapan.idtalent, Hasillatihanpercakapan.wpm.label("score_val"),
            Hasillatihanpercakapan.waktulatihan, literal_column("'Speaking'").label("category"),
            literal_column("'Conversation'").label("type")
        ).where(date_filter(Hasillatihanpercakapan.waktulatihan))

        q_int = select(
            Hasillatihaninterview.idtalent, Hasillatihaninterview.wpm.label("score_val"),
            Hasillatihaninterview.waktulatihan, literal_column("'Speaking'").label("category"),
            literal_column("'Interview'").label("type")
        ).where(date_filter(Hasillatihaninterview.waktulatihan))

        union_q = union_all(q_phoneme, q_exam, q_conv, q_int).alias("activities")
        
        final_query = (
            select(union_q, Talent.nama)
            .join(Talent, Talent.idtalent == union_q.c.idtalent)
            .order_by(desc(union_q.c.waktulatihan))
            .limit(limit)
        )

        result = await self.db.execute(final_query)
        
        formatted_results = []
        for row in result:
            score_val = row.score_val if row.score_val is not None else 0
            score_display = f"{score_val:.0f} WPM" if row.type in ['Conversation', 'Interview'] else f"{score_val:.0f}%"
            
            formatted_results.append({
                "talentId": row.idtalent,
                "talentName": row.nama,
                "activityType": f"{row.type} Practice" if row.type == "Phoneme" else row.type,
                "category": row.category or "General",
                "score": score_display,
                "date": row.waktulatihan
            })
            
        return formatted_results

    # --- Other methods (Specific User & Leaderboard) remain same for brevity, ensure they are in file ---
    async def get_user_activity_dates(self, talent_id: int):
        q1 = select(Hasillatihanfonem.waktulatihan).where(Hasillatihanfonem.idtalent == talent_id)
        q2 = select(Ujianfonem.waktuujian).where(Ujianfonem.idtalent == talent_id)
        q3 = select(Hasillatihanpercakapan.waktulatihan).where(Hasillatihanpercakapan.idtalent == talent_id)
        q4 = select(Hasillatihaninterview.waktulatihan).where(Hasillatihaninterview.idtalent == talent_id)
        union_q = union_all(q1, q2, q3, q4)
        result = await self.db.execute(union_q)
        return [row[0] for row in result.all()]

    async def get_user_avg_pronunciation(self, talent_id: int) -> float:
        query = select(func.avg(Hasillatihanfonem.nilai)).where(Hasillatihanfonem.idtalent == talent_id)
        return await self.db.scalar(query) or 0.0

    async def get_user_conversation_stats(self, talent_id: int):
        query = select(func.avg(Hasillatihanpercakapan.wpm), func.count(Hasillatihanpercakapan.idhasilpercakapan)).where(Hasillatihanpercakapan.idtalent == talent_id)
        result = await self.db.execute(query)
        row = result.first()
        return {"avg_wpm": row[0] or 0.0, "count": row[1] or 0}

    async def get_user_interview_stats(self, talent_id: int):
        query = select(func.avg(Hasillatihaninterview.wpm), func.count(Hasillatihaninterview.idhasilinterview)).where(Hasillatihaninterview.idtalent == talent_id)
        result = await self.db.execute(query)
        row = result.first()
        return {"avg_wpm": row[0] or 0.0, "count": row[1] or 0}

    async def get_user_phoneme_counts(self, talent_id: int):
        query = select(func.count(func.distinct(Hasillatihanfonem.idsoal))).where(Hasillatihanfonem.idtalent == talent_id)
        return await self.db.scalar(query) or 0

    async def get_all_talents(self, search: str = None):
        query = select(Talent)
        if search: query = query.filter(Talent.nama.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_all_activities_dates(self):
        q1 = select(Hasillatihanfonem.idtalent, Hasillatihanfonem.waktulatihan)
        q2 = select(Ujianfonem.idtalent, Ujianfonem.waktuujian.label("waktulatihan"))
        q3 = select(Hasillatihanpercakapan.idtalent, Hasillatihanpercakapan.waktulatihan)
        q4 = select(Hasillatihaninterview.idtalent, Hasillatihaninterview.waktulatihan)
        union_q = union_all(q1, q2, q3, q4).alias("act")
        query = select(union_q.c.idtalent, union_q.c.waktulatihan)
        result = await self.db.execute(query)
        return result.all()

    async def get_highest_scoring_phoneme(self, type_latihan: str):
        query = (select(Talent.idtalent, Talent.nama, Talent.email, func.count(func.distinct(Hasillatihanfonem.idsoal)).label('attempted'), func.avg(Hasillatihanfonem.nilai).label('avg_score')).join(Hasillatihanfonem, Talent.idtalent == Hasillatihanfonem.idtalent).where(Hasillatihanfonem.typelatihan == type_latihan).group_by(Talent.idtalent))
        result = await self.db.execute(query)
        return result.all()

    async def get_highest_scoring_exam(self):
        query = (select(Talent.idtalent, Talent.nama, Talent.email, func.count(func.distinct(Ujianfonem.kategori)).label('categories_attempted'), func.avg(Ujianfonem.nilai).label('avg_score'), func.count(Ujianfonem.idujian).label('total_attempts')).join(Ujianfonem, Talent.idtalent == Ujianfonem.idtalent).where(Ujianfonem.nilai != None).group_by(Talent.idtalent))
        result = await self.db.execute(query)
        return result.all()

    async def get_highest_scoring_conversation(self):
        query = (select(Talent.idtalent, Talent.nama, Talent.email, func.avg(Hasillatihanpercakapan.wpm).label('avg_wpm'), func.count(Hasillatihanpercakapan.idhasilpercakapan).label('total_attempts'), func.max(Hasillatihanpercakapan.waktulatihan).label('last_date')).join(Hasillatihanpercakapan, Talent.idtalent == Hasillatihanpercakapan.idtalent).group_by(Talent.idtalent))
        result = await self.db.execute(query)
        return result.all()

    async def get_highest_scoring_interview(self):
        query = (select(Talent.idtalent, Talent.nama, Talent.email, func.avg(Hasillatihaninterview.wpm).label('avg_wpm'), func.count(Hasillatihaninterview.idhasilinterview).label('total_attempts'), func.max(Hasillatihaninterview.waktulatihan).label('last_date')).join(Hasillatihaninterview, Talent.idtalent == Hasillatihaninterview.idtalent).group_by(Talent.idtalent))
        result = await self.db.execute(query)
        return result.all()

    async def get_admin_by_email(self, email: str):
        result = await self.db.execute(select(Manajemen).where(Manajemen.email == email))
        return result.scalar_one_or_none()