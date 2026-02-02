from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Ujianfonem, Detailujianfonem, Materiujian, Materiujiankalimat
from datetime import datetime

class ExamRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_exam(self, talent_id: int, exam_id: int):
        """Mencari ujian yang sedang berlangsung (nilai masih None)"""
        query = select(Ujianfonem).where(
            and_(
                Ujianfonem.idtalent == talent_id,
                Ujianfonem.idmateriujian == exam_id,
                Ujianfonem.nilai == None
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_exam_by_id(self, ujian_id: int):
        return await self.db.get(Ujianfonem, ujian_id)

    async def create_exam_entry(self, talent_id: int, exam_id: int, category: str):
        """Membuat sesi ujian baru"""
        exam = Ujianfonem(
            idmateriujian=exam_id,
            idtalent=talent_id,
            kategori=category,
            nilai=None,
            waktuujian=datetime.utcnow()
        )
        self.db.add(exam)
        await self.db.commit()
        await self.db.refresh(exam)
        return exam

    async def get_answered_question_ids(self, ujian_id: int):
        """Mengambil ID soal yang sudah dijawab dalam sesi ini"""
        query = select(Detailujianfonem.idsoal).where(Detailujianfonem.idujian == ujian_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_remaining_questions(self, exam_id: int, answered_ids: list):
        """Mengambil soal yang belum dikerjakan"""
        query = select(Materiujiankalimat).where(Materiujiankalimat.idmateriujian == exam_id)
        if answered_ids:
            query = query.where(Materiujiankalimat.idmateriujiankalimat.notin_(answered_ids))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_materi_header(self, exam_id: int):
        return await self.db.get(Materiujian, exam_id)

    async def get_materi_kalimat(self, soal_id: int):
        return await self.db.get(Materiujiankalimat, soal_id)

    async def save_detail_answer(self, ujian_id: int, soal_id: int, score: float):
        """Menyimpan jawaban per soal"""
        detail = Detailujianfonem(idujian=ujian_id, idsoal=soal_id, nilai=score)
        self.db.add(detail)
        await self.db.commit()
        return detail

    async def get_exam_details_with_questions(self, ujian_id: int):
        """Mengambil detail jawaban beserta teks soalnya untuk result"""
        query = (
            select(Detailujianfonem, Materiujiankalimat.kalimat)
            .join(Materiujiankalimat, Detailujianfonem.idsoal == Materiujiankalimat.idmateriujiankalimat)
            .where(Detailujianfonem.idujian == ujian_id)
        )
        result = await self.db.execute(query)
        return result.all()

    async def update_final_score(self, ujian_id: int, score: float):
        """Update nilai akhir ujian"""
        ujian = await self.get_exam_by_id(ujian_id)
        if ujian:
            ujian.nilai = score
            await self.db.commit()
            await self.db.refresh(ujian)
        return ujian