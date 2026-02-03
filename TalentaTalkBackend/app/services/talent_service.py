from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.talent_repository import TalentRepository
from app.schemas.talent import TalentUpdate
from app.schemas.auth import TalentCreate
from app.core.exceptions import NotFoundError, AppError, DuplicateError
from app.utils.time_utils import TimeUtils
from passlib.context import CryptContext
import pandas as pd
import io

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TalentService:
    def __init__(self, db: AsyncSession):
        self.repo = TalentRepository(db)

    async def get_talents_list(self, page: int, limit: int, search: str):
        skip = (page - 1) * limit
        talents, total = await self.repo.get_talents_paginated(skip, limit, search)
        results = []
        for t in talents:
            stats = await self.repo.get_talent_progress_stats(t.idtalent)
            latest = stats['latest_exam'] if stats['latest_exam'] is not None else 0
            highest = stats['highest_exam'] if stats['highest_exam'] is not None else 0
            results.append({
                "id": t.idtalent, "talentName": t.nama, "email": t.email, "role": t.role,
                "pretest": f"{t.pretest_score:.0f}%" if t.pretest_score is not None else "N/A",
                "highestExam": f"{highest:.0f}%", "progress": f"{stats['progress']:.0f}%"
            })
        return {"data": results, "total": total, "page": page, "size": limit}

    async def get_talent_detail(self, talent_id: int):
        talent = await self.repo.get_by_id(talent_id)
        if not talent: raise NotFoundError("Talent")
        stats = await self.repo.get_talent_progress_stats(talent_id)
        latest = stats['latest_exam'] if stats['latest_exam'] is not None else 0
        highest = stats['highest_exam'] if stats['highest_exam'] is not None else 0
        return {
            "talentId": f"TLT{talent.idtalent:03d}", "nama": talent.nama, "role": talent.role, "email": talent.email,
            "lastExam": f"{latest:.0f}%" if stats['latest_exam'] is not None else "N/A",
            "highestExam": f"{highest:.0f}%" if stats['highest_exam'] is not None else "N/A",
            "progress": f"{stats['progress']:.0f}%"
        }
        
    async def create_talent(self, data: TalentCreate):
        # 1. Cek Email Duplikat
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise DuplicateError(f"Email {data.email} sudah terdaftar")
        
        # 2. Hash Password
        hashed_pw = pwd_context.hash(data.password)
        
        # 3. Simpan ke DB
        new_talent_data = {
            "nama": data.nama,
            "email": data.email,
            "password": hashed_pw,
            "role": data.role
        }
        return await self.repo.create(new_talent_data)

    async def delete_talent(self, talent_id: int):
        talent = await self.repo.get_by_id(talent_id)
        if not talent: raise NotFoundError("Talent")
        await self.repo.delete(talent)
        return True

    async def update_talent(self, talent_id: int, data: TalentUpdate):
        talent = await self.repo.get_by_id(talent_id)
        if not talent: raise NotFoundError("Talent")
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(talent, update_data)

    async def change_password(self, talent_id: int, new_password: str):
        talent = await self.repo.get_by_id(talent_id)
        if not talent: raise NotFoundError("Talent")
        hashed = pwd_context.hash(new_password)
        await self.repo.update(talent, {"password": hashed})
        return True

    async def import_talents_from_excel(self, file_content: bytes):
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            required = ['nama', 'email', 'role', 'password']
            df.columns = df.columns.str.lower().str.strip()
            missing = [col for col in required if col not in df.columns]
            if missing: raise AppError(status_code=400, detail=f"Missing columns: {', '.join(missing)}")
            success, errors = 0, []
            for idx, row in df.iterrows():
                try:
                    email = str(row['email']).strip()
                    if await self.repo.get_by_email(email): raise ValueError(f"Email {email} already exists")
                    data = {"nama": str(row['nama']).strip(), "email": email, "role": str(row['role']).strip(), "password": pwd_context.hash(str(row['password']).strip())}
                    await self.repo.create(data)
                    success += 1
                except Exception as e:
                    errors.append({"row": idx + 2, "error": str(e)})
            return {"successCount": success, "errorCount": len(errors), "errors": errors}
        except Exception as e:
            raise AppError(status_code=400, detail=f"Import failed: {str(e)}")

    async def get_phoneme_progress(self, talent_id: int, type_latihan: str, page: int, limit: int):
        skip = (page - 1) * limit
        items, total = await self.repo.get_phoneme_history_paginated(talent_id, type_latihan, skip, limit)
        data = []
        for item in items:
            data.append({
                "phonemeCategory": item["category"], "content": item["content"],
                "score": f"{item['score']:.0f}%", "date": TimeUtils.format_to_wib(item["date"])
            })
        return {"data": data, "total": total, "page": page}

    async def get_exam_progress(self, talent_id: int, page: int, limit: int):
        skip = (page - 1) * limit
        exams, total = await self.repo.get_exam_history_paginated(talent_id, skip, limit)
        data = []
        for ex in exams:
            data.append({
                "examId": ex.idujian, "phonemeCategory": ex.kategori,
                "score": f"{ex.nilai or 0:.0f}%", "date": TimeUtils.format_to_wib(ex.waktuujian)
            })
        return {"data": data, "total": total, "page": page}

    async def get_exam_attempt_detail(self, talent_id: int, attempt_id: int):
        exam, details = await self.repo.get_exam_attempt_detail(talent_id, attempt_id)
        if not exam: raise NotFoundError("Exam Attempt")
        sentences_data = []
        for row in details:
            detail, kalimat = row
            sentences_data.append({"sentence": kalimat.kalimat, "phonemeTranscription": kalimat.fonem, "score": f"{detail.nilai or 0:.0f}%"})
        return {
            "attemptId": f"ATT{exam.idujian:03d}", "phonemeCategory": exam.kategori,
            "totalScore": f"{exam.nilai or 0:.0f}%", "date": TimeUtils.format_to_wib(exam.waktuujian),
            "sentences": sentences_data
        }

    async def get_conversation_progress(self, talent_id: int, page: int, limit: int):
        skip = (page - 1) * limit
        items, total = await self.repo.get_conversation_history_paginated(talent_id, skip, limit)
        data = []
        for row in items:
            res, topic = row
            data.append({
                "topic": topic or "General", "wpm": f"{res.wpm or 0:.0f}",
                "grammarIssue": res.grammar or "No issues", "date": TimeUtils.format_to_wib(res.waktulatihan)
            })
        return {"data": data, "total": total, "page": page}

    async def get_interview_progress(self, talent_id: int, page: int, limit: int):
        skip = (page - 1) * limit
        items, total = await self.repo.get_interview_history_paginated(talent_id, skip, limit)
        data = []
        for idx, item in enumerate(items):
            attempt_no = total - skip - idx
            data.append({
                "attempt": attempt_no, "attemptId": item.idhasilinterview, "wordProducePerMinute": f"{item.wpm or 0:.0f}",
                "feedback": item.feedback[:50] + "..." if item.feedback else "No feedback", "date": TimeUtils.format_to_wib(item.waktulatihan)
            })
        return {"data": data, "total": total, "page": page}

    async def get_interview_detail(self, talent_id: int, attempt_id: int):
        interview = await self.repo.get_interview_detail(talent_id, attempt_id)
        if not interview: raise NotFoundError("Interview")
        return {"attemptId": attempt_id, "date": TimeUtils.format_to_wib(interview.waktulatihan), "feedback": interview.feedback, "wpm": f"{interview.wpm:.0f}", "grammar": interview.grammar}