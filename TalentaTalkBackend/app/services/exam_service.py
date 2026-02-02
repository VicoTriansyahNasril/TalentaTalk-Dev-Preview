from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.exam_repository import ExamRepository
from app.services.audio_service import AudioService
from app.utils.phoneme_utils import PhonemeMatcher
from app.core.exceptions import NotFoundError, AppError

class ExamService:
    def __init__(self, db: AsyncSession):
        self.repo = ExamRepository(db)

    async def start_exam_session(self, talent_id: int, material_exam_id: int):
        # 1. Cek materi ada tidak
        materi = await self.repo.get_materi_header(material_exam_id)
        if not materi:
            raise NotFoundError("Materi Ujian")

        # 2. Cek apakah ada sesi ujian yang belum selesai (nilai is None)
        ujian = await self.repo.get_active_exam(talent_id, material_exam_id)
        
        # Jika tidak ada sesi aktif, buat baru
        if not ujian:
            ujian = await self.repo.create_exam_entry(talent_id, material_exam_id, materi.kategori)

        # 3. Cek soal mana saja yang sudah dikerjakan
        answered_ids = await self.repo.get_answered_question_ids(ujian.idujian)
        
        # 4. Jika sudah 10 soal terjawab, berarti ujian selesai
        # (Dalam kasus edge case dimana status belum terupdate)
        if len(answered_ids) >= 10:
            # Trigger finish calculation just in case
            await self.finish_exam(ujian.idujian)
            return {"message": "Ujian telah selesai", "id_ujianfonem": ujian.idujian, "data": []}

        # 5. Ambil sisa soal yang belum dikerjakan
        remaining_q = await self.repo.get_remaining_questions(material_exam_id, answered_ids)
        
        # Format data untuk mobile
        data = [
            {
                "id": q.idmateriujiankalimat, 
                "kalimat": q.kalimat, 
                "fonem": q.fonem,
                "kategori": materi.kategori # Tambahan info kategori
            } 
            for q in remaining_q
        ]
        
        return {
            "id_ujianfonem": ujian.idujian,
            "remaining": len(remaining_q),
            "data": data
        }

    async def process_answer(self, ujian_id: int, soal_id: int, audio_bytes: bytes):
        # 1. Ambil kalimat target
        soal = await self.repo.get_materi_kalimat(soal_id)
        if not soal: raise NotFoundError("Soal")
        
        # 2. Transkripsi & Scoring (Heavy Task)
        user_phonemes = await AudioService.transcribe(audio_bytes)
        alignment = PhonemeMatcher.align_phonemes(soal.fonem, user_phonemes)
        score = PhonemeMatcher.calculate_accuracy(alignment)
        
        # 3. Simpan Detail Jawaban
        await self.repo.save_detail_answer(ujian_id, soal_id, score)
        
        return {
            "similarity_percent": f"{score}%",
            "phoneme_comparison": alignment,
            "user_phonemes": user_phonemes,
            "target_phonemes": soal.fonem
        }

    async def finish_exam(self, ujian_id: int):
        """Menghitung nilai akhir dan menutup sesi ujian"""
        details_with_q = await self.repo.get_exam_details_with_questions(ujian_id)
        
        if not details_with_q:
            raise AppError(status_code=400, detail="Belum ada soal yang dikerjakan")
            
        # Hitung rata-rata
        total_score = sum(row.Detailujianfonem.nilai for row in details_with_q)
        count = len(details_with_q)
        avg_score = round(total_score / count, 2) if count > 0 else 0
        
        # Update header ujian
        ujian = await self.repo.update_final_score(ujian_id, avg_score)
        
        # Format detail untuk response result screen
        detail_list = [
            {
                "idsoal": row.Detailujianfonem.idsoal,
                "kalimat": row.kalimat,
                "nilai": row.Detailujianfonem.nilai
            }
            for row in details_with_q
        ]

        return {
            "success": True,
            "id_ujian": ujian.idujian,
            "kategori": ujian.kategori,
            "jumlah_soal": count,
            "nilai_rata_rata": avg_score,
            "detail": detail_list
        }