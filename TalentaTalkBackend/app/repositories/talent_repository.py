from sqlalchemy import select, func, or_, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.models import (
    Talent, Ujianfonem, Hasillatihanfonem, Materifonemkata, 
    Materifonemkalimat, Hasillatihanpercakapan, Materipercakapan,
    Hasillatihaninterview, Detailujianfonem, Materiujiankalimat
)

class TalentRepository(BaseRepository[Talent]):
    def __init__(self, db: AsyncSession):
        super().__init__(Talent, db)

    async def get_by_email(self, email: str):
        query = select(Talent).where(Talent.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_talents_paginated(self, skip: int = 0, limit: int = 10, search: str = None):
        query = select(Talent)
        if search:
            search_filter = or_(Talent.nama.ilike(f"%{search}%"), Talent.email.ilike(f"%{search}%"))
            query = query.filter(search_filter)
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        query = query.order_by(Talent.idtalent.asc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_talent_progress_stats(self, talent_id: int):
        q_exam = select(Ujianfonem.nilai).where(Ujianfonem.idtalent == talent_id).order_by(desc(Ujianfonem.waktuujian)).limit(1)
        latest_exam = await self.db.scalar(q_exam)
        q_high = select(func.max(Ujianfonem.nilai)).where(Ujianfonem.idtalent == talent_id)
        highest_exam = await self.db.scalar(q_high)
        total_word = await self.db.scalar(select(func.count(Materifonemkata.idmaterifonemkata)))
        total_sent = await self.db.scalar(select(func.count(Materifonemkalimat.idmaterifonemkalimat)))
        total_materi = (total_word or 0) + (total_sent or 0)
        q_done = select(func.count(func.distinct(Hasillatihanfonem.idsoal))).where(Hasillatihanfonem.idtalent == talent_id)
        done = await self.db.scalar(q_done) or 0
        progress_percent = (done / total_materi * 100) if total_materi > 0 else 0
        return {"latest_exam": latest_exam, "highest_exam": highest_exam, "progress": progress_percent}

    async def get_phoneme_history_paginated(self, talent_id: int, type_latihan: str, skip: int, limit: int):
        base_query = select(Hasillatihanfonem).where(and_(Hasillatihanfonem.idtalent == talent_id, Hasillatihanfonem.typelatihan == type_latihan))
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.db.scalar(count_query) or 0
        query = base_query.order_by(desc(Hasillatihanfonem.waktulatihan)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()
        enriched = []
        for item in items:
            text_val = "Unknown"
            category = "General"
            if type_latihan == "Word":
                text_val = await self.db.scalar(select(Materifonemkata.kata).where(Materifonemkata.idmaterifonemkata == item.idsoal))
                category = await self.db.scalar(select(Materifonemkata.kategori).where(Materifonemkata.idmaterifonemkata == item.idsoal))
            else:
                text_val = await self.db.scalar(select(Materifonemkalimat.kalimat).where(Materifonemkalimat.idmaterifonemkalimat == item.idsoal))
                category = await self.db.scalar(select(Materifonemkalimat.kategori).where(Materifonemkalimat.idmaterifonemkalimat == item.idsoal))
            enriched.append({"category": category, "content": text_val, "score": item.nilai, "date": item.waktulatihan})
        return enriched, total

    async def get_exam_history_paginated(self, talent_id: int, skip: int, limit: int):
        base_query = select(Ujianfonem).where(Ujianfonem.idtalent == talent_id)
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.db.scalar(count_query) or 0
        query = base_query.order_by(desc(Ujianfonem.waktuujian)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_exam_attempt_detail(self, talent_id: int, attempt_id: int):
        exam = await self.db.get(Ujianfonem, attempt_id)
        if not exam or exam.idtalent != talent_id: return None, None
        q_details = select(Detailujianfonem, Materiujiankalimat).join(Materiujiankalimat, Detailujianfonem.idsoal == Materiujiankalimat.idmateriujiankalimat).where(Detailujianfonem.idujian == attempt_id)
        result = await self.db.execute(q_details)
        return exam, result.all()

    async def get_conversation_history_paginated(self, talent_id: int, skip: int, limit: int):
        base_query = select(Hasillatihanpercakapan, Materipercakapan.topic).join(Materipercakapan, Hasillatihanpercakapan.idmateripercakapan == Materipercakapan.idmateripercakapan).where(Hasillatihanpercakapan.idtalent == talent_id)
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.db.scalar(count_query) or 0
        query = base_query.order_by(desc(Hasillatihanpercakapan.waktulatihan)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.all(), total

    async def get_interview_history_paginated(self, talent_id: int, skip: int, limit: int):
        base_query = select(Hasillatihaninterview).where(Hasillatihaninterview.idtalent == talent_id)
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.db.scalar(count_query) or 0
        query = base_query.order_by(desc(Hasillatihaninterview.waktulatihan)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all(), total
    
    async def get_interview_detail(self, talent_id: int, attempt_id: int):
        query = select(Hasillatihaninterview).where(and_(Hasillatihaninterview.idhasilinterview == attempt_id, Hasillatihaninterview.idtalent == talent_id))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()