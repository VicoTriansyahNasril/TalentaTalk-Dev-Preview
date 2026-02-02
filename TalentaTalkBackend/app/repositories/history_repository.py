from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import (
    Hasillatihanfonem, Hasillatihanpercakapan, Hasillatihaninterview, 
    Ujianfonem, Detailujianfonem, Materifonemkata, Materifonemkalimat, 
    Materipercakapan, Materiujiankalimat
)
from datetime import datetime, timedelta

class HistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_phoneme_history(self, talent_id: int, days_back: int = 7, skip: int = 0, limit: int = 10):
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        query = (
            select(Hasillatihanfonem)
            .where(
                Hasillatihanfonem.idtalent == talent_id,
                Hasillatihanfonem.waktulatihan >= cutoff
            )
            .order_by(desc(Hasillatihanfonem.waktulatihan))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        # Perlu manual fetch nama soal karena polimorfik (Word/Sentence)
        enriched_items = []
        for item in items:
            soal_text = "Unknown"
            if item.typelatihan == "Word":
                q = select(Materifonemkata.kata).where(Materifonemkata.idmaterifonemkata == item.idsoal)
                soal_text = await self.db.scalar(q)
            elif item.typelatihan == "Sentence":
                q = select(Materifonemkalimat.kalimat).where(Materifonemkalimat.idmaterifonemkalimat == item.idsoal)
                soal_text = await self.db.scalar(q)
            
            enriched_items.append({
                "raw": item,
                "soal_text": soal_text
            })
            
        return enriched_items

    async def get_conversation_history(self, talent_id: int, days_back: int = 7):
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        query = (
            select(Hasillatihanpercakapan, Materipercakapan.topic)
            .join(Materipercakapan, Materipercakapan.idmateripercakapan == Hasillatihanpercakapan.idmateripercakapan)
            .where(
                Hasillatihanpercakapan.idtalent == talent_id,
                Hasillatihanpercakapan.waktulatihan >= cutoff
            )
            .order_by(desc(Hasillatihanpercakapan.waktulatihan))
        )
        result = await self.db.execute(query)
        return result.all() # Returns tuples (Model, topic_string)

    async def get_interview_history(self, talent_id: int, days_back: int = 7):
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        query = (
            select(Hasillatihaninterview)
            .where(
                Hasillatihaninterview.idtalent == talent_id,
                Hasillatihaninterview.waktulatihan >= cutoff
            )
            .order_by(desc(Hasillatihaninterview.waktulatihan))
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_exam_history(self, talent_id: int, days_back: int = 7):
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        query = (
            select(Ujianfonem)
            .where(
                Ujianfonem.idtalent == talent_id,
                Ujianfonem.waktuujian >= cutoff
            )
            .order_by(desc(Ujianfonem.waktuujian))
        )
        result = await self.db.execute(query)
        exams = result.scalars().all()
        
        # Fetch details for each exam
        history_data = []
        for exam in exams:
            q_detail = (
                select(Detailujianfonem, Materiujiankalimat.kalimat)
                .join(Materiujiankalimat, Detailujianfonem.idsoal == Materiujiankalimat.idmateriujiankalimat)
                .where(Detailujianfonem.idujian == exam.idujian)
            )
            details_res = await self.db.execute(q_detail)
            details = [{"score": r.Detailujianfonem.nilai, "kalimat": r.kalimat} for r in details_res]
            
            history_data.append({
                "exam": exam,
                "details": details
            })
            
        return history_data