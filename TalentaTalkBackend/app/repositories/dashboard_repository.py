from sqlalchemy import select, func, desc, union_all, literal_column, and_, cast, Date, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import (
    Talent, Materifonemkata, Materifonemkalimat, Materiujian, Materiinterview,
    Hasillatihanfonem, Hasillatihanpercakapan, Hasillatihaninterview, Ujianfonem, Manajemen
)
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pytz

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

    async def get_recent_activities(self, limit: int = 10, days_back: int = 30, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        if start_date and end_date:
            cutoff_start, cutoff_end = start_date, end_date
        else:
            cutoff_start = datetime.utcnow() - timedelta(days=days_back)
            cutoff_end = datetime.utcnow() + timedelta(days=1)

        def date_filter(col): return col.between(cutoff_start, cutoff_end)

        q1 = select(Hasillatihanfonem.idtalent, Hasillatihanfonem.nilai.label("score"), Hasillatihanfonem.waktulatihan, Hasillatihanfonem.typelatihan.label("category"), literal_column("'Phoneme'").label("type")).where(date_filter(Hasillatihanfonem.waktulatihan))
        q2 = select(Ujianfonem.idtalent, Ujianfonem.nilai.label("score"), Ujianfonem.waktuujian.label("waktulatihan"), Ujianfonem.kategori.label("category"), literal_column("'Exam'").label("type")).where(date_filter(Ujianfonem.waktuujian))
        q3 = select(Hasillatihanpercakapan.idtalent, Hasillatihanpercakapan.wpm.label("score"), Hasillatihanpercakapan.waktulatihan, literal_column("'Conversation'").label("category"), literal_column("'Conversation'").label("type")).where(date_filter(Hasillatihanpercakapan.waktulatihan))
        q4 = select(Hasillatihaninterview.idtalent, Hasillatihaninterview.wpm.label("score"), Hasillatihaninterview.waktulatihan, literal_column("'Interview'").label("category"), literal_column("'Interview'").label("type")).where(date_filter(Hasillatihaninterview.waktulatihan))

        union_q = union_all(q1, q2, q3, q4).alias("act")
        result = await self.db.execute(select(union_q, Talent.nama).join(Talent, Talent.idtalent == union_q.c.idtalent).order_by(desc(union_q.c.waktulatihan)).limit(limit))
        
        return [{"talentId": r.idtalent, "talentName": r.nama, "activityType": r.type, "category": r.category, "score": r.score, "date": r.waktulatihan} for r in result]
    async def get_user_recent_activities_mobile(self, talent_id: int, limit: int = 5):
        """Mengambil data gabungan untuk Home Screen Mobile (Recent Activities)"""
        q1 = select(
            Hasillatihanfonem.idhasilfonem.label("id"),
            literal_column("'Phoneme Practice'").label("title"),
            literal_column("'phoneme'").label("type"),
            Hasillatihanfonem.typelatihan.label("category"),
            Hasillatihanfonem.nilai.label("score"),
            Hasillatihanfonem.waktulatihan
        ).where(Hasillatihanfonem.idtalent == talent_id)

        q2 = select(
            Ujianfonem.idujian.label("id"),
            literal_column("'Phoneme Exam'").label("title"),
            literal_column("'exam'").label("type"),
            Ujianfonem.kategori.label("category"),
            Ujianfonem.nilai.label("score"),
            Ujianfonem.waktuujian.label("waktulatihan")
        ).where(Ujianfonem.idtalent == talent_id)

        q3 = select(
            Hasillatihanpercakapan.idhasilpercakapan.label("id"),
            literal_column("'Conversation Practice'").label("title"),
            literal_column("'conversation'").label("type"),
            literal_column("'General'").label("category"),
            Hasillatihanpercakapan.wpm.label("score"),
            Hasillatihanpercakapan.waktulatihan
        ).where(Hasillatihanpercakapan.idtalent == talent_id)

        q4 = select(
            Hasillatihaninterview.idhasilinterview.label("id"),
            literal_column("'Interview Practice'").label("title"),
            literal_column("'interview'").label("type"),
            literal_column("'General'").label("category"),
            Hasillatihaninterview.wpm.label("score"),
            Hasillatihaninterview.waktulatihan
        ).where(Hasillatihaninterview.idtalent == talent_id)

        union_q = union_all(q1, q2, q3, q4).alias("user_activities")
        
        query = select(union_q).order_by(desc(union_q.c.waktulatihan)).limit(limit)
        result = await self.db.execute(query)
        
        activities = []
        for row in result:
            dt = row.waktulatihan
            if dt.tzinfo is None: dt = pytz.utc.localize(dt)
            wib_time = dt.astimezone(pytz.timezone('Asia/Jakarta'))
            
            activities.append({
                "id": row.id,
                "title": row.title,
                "type": row.type,
                "category": row.category,
                "score": float(row.score) if row.score is not None else 0.0,
                "date": wib_time.strftime("%Y-%m-%d"),
                "time": wib_time.strftime("%H:%M"),
                "waktulatihan": row.waktulatihan.isoformat()
            })
        return activities

    async def calculate_learning_streak(self, talent_id: int):
        """Menghitung streak harian secara dinamis dari database"""
        q1 = select(cast(Hasillatihanfonem.waktulatihan, Date)).where(Hasillatihanfonem.idtalent == talent_id)
        q2 = select(cast(Ujianfonem.waktuujian, Date)).where(Ujianfonem.idtalent == talent_id)
        q3 = select(cast(Hasillatihanpercakapan.waktulatihan, Date)).where(Hasillatihanpercakapan.idtalent == talent_id)
        q4 = select(cast(Hasillatihaninterview.waktulatihan, Date)).where(Hasillatihaninterview.idtalent == talent_id)
        
        union_q = union_all(q1, q2, q3, q4).alias("dates")
        
        query = select(distinct(union_q.c.waktulatihan)).order_by(desc(union_q.c.waktulatihan))
        
        result = await self.db.execute(query)
        dates = [row[0] for row in result.all()]

        if not dates:
            return 0, 0

        current_streak = 0
        today = datetime.now(pytz.timezone('Asia/Jakarta')).date()
        
        last_activity = dates[0]
        if last_activity == today or last_activity == today - timedelta(days=1):
            current_streak = 1
            for i in range(len(dates) - 1):
                if (dates[i] - dates[i+1]).days == 1:
                    current_streak += 1
                else:
                    break
        
        start_of_week = today - timedelta(days=today.weekday())
        weekly_count = sum(1 for d in dates if d >= start_of_week)

        return current_streak, weekly_count

    async def get_user_avg_pronunciation(self, talent_id: int) -> float:
        return await self.db.scalar(select(func.avg(Hasillatihanfonem.nilai)).where(Hasillatihanfonem.idtalent == talent_id)) or 0.0

    async def get_user_conversation_stats(self, talent_id: int):
        res = await self.db.execute(select(func.avg(Hasillatihanpercakapan.wpm), func.count(Hasillatihanpercakapan.idhasilpercakapan)).where(Hasillatihanpercakapan.idtalent == talent_id))
        row = res.first()
        return {"avg_wpm": row[0] or 0.0, "count": row[1] or 0}

    async def get_user_interview_stats(self, talent_id: int):
        res = await self.db.execute(select(func.avg(Hasillatihaninterview.wpm), func.count(Hasillatihaninterview.idhasilinterview)).where(Hasillatihaninterview.idtalent == talent_id))
        row = res.first()
        return {"avg_wpm": row[0] or 0.0, "count": row[1] or 0}

    async def get_user_phoneme_counts(self, talent_id: int):
        return await self.db.scalar(select(func.count(Hasillatihanfonem.idhasilfonem)).where(Hasillatihanfonem.idtalent == talent_id)) or 0

    async def get_user_exam_summary(self, talent_id: int):
        latest_score = await self.db.scalar(select(Ujianfonem.nilai).where(Ujianfonem.idtalent == talent_id).order_by(desc(Ujianfonem.waktuujian)).limit(1))
        total_exams = await self.db.scalar(select(func.count(Ujianfonem.idujian)).where(Ujianfonem.idtalent == talent_id))
        avg_score = await self.db.scalar(select(func.avg(Ujianfonem.nilai)).where(Ujianfonem.idtalent == talent_id))
        last_date = await self.db.scalar(select(Ujianfonem.waktuujian).where(Ujianfonem.idtalent == talent_id).order_by(desc(Ujianfonem.waktuujian)).limit(1))
        
        days_ago = 0
        if last_date:
            days_ago = (datetime.utcnow() - last_date).days

        return {
            "latest_exam_score": latest_score or 0.0,
            "total_exams": total_exams or 0,
            "average_exam_score": avg_score or 0.0,
            "last_exam_days_ago": days_ago
        }
    
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
        return (await self.db.execute(union_all(q1, q2, q3, q4))).all()

    async def get_highest_scoring_phoneme(self, type_latihan: str):
        return (await self.db.execute(select(Talent.idtalent, Talent.nama, Talent.email, func.count(func.distinct(Hasillatihanfonem.idsoal)).label('attempted'), func.avg(Hasillatihanfonem.nilai).label('avg_score')).join(Hasillatihanfonem, Talent.idtalent == Hasillatihanfonem.idtalent).where(Hasillatihanfonem.typelatihan == type_latihan).group_by(Talent.idtalent))).all()

    async def get_highest_scoring_exam(self):
        return (await self.db.execute(select(Talent.idtalent, Talent.nama, Talent.email, func.count(func.distinct(Ujianfonem.kategori)).label('categories_attempted'), func.avg(Ujianfonem.nilai).label('avg_score'), func.count(Ujianfonem.idujian).label('total_attempts')).join(Ujianfonem, Talent.idtalent == Ujianfonem.idtalent).where(Ujianfonem.nilai != None).group_by(Talent.idtalent))).all()

    async def get_highest_scoring_conversation(self):
        return (await self.db.execute(select(Talent.idtalent, Talent.nama, Talent.email, func.avg(Hasillatihanpercakapan.wpm).label('avg_wpm'), func.count(Hasillatihanpercakapan.idhasilpercakapan).label('total_attempts'), func.max(Hasillatihanpercakapan.waktulatihan).label('last_date')).join(Hasillatihanpercakapan, Talent.idtalent == Hasillatihanpercakapan.idtalent).group_by(Talent.idtalent))).all()

    async def get_highest_scoring_interview(self):
        return (await self.db.execute(select(Talent.idtalent, Talent.nama, Talent.email, func.avg(Hasillatihaninterview.wpm).label('avg_wpm'), func.count(Hasillatihaninterview.idhasilinterview).label('total_attempts'), func.max(Hasillatihaninterview.waktulatihan).label('last_date')).join(Hasillatihaninterview, Talent.idtalent == Hasillatihaninterview.idtalent).group_by(Talent.idtalent))).all()

    async def get_admin_by_email(self, email: str):
        return (await self.db.execute(select(Manajemen).where(Manajemen.email == email))).scalar_one_or_none()