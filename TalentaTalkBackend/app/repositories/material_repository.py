from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.models import Materipercakapan, Materifonemkata, Materifonemkalimat, Materiujian, Materiujiankalimat, Materiinterview
from app.core.exceptions import DuplicateError

class MaterialRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- READ METHODS (General) ---
    async def get_random_topic(self):
        query = select(Materipercakapan).order_by(func.random()).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_phoneme_content(self, id: int, type: str):
        if type == "word":
            query = select(Materifonemkata).where(Materifonemkata.idmaterifonemkata == id)
        else:
            query = select(Materifonemkalimat).where(Materifonemkalimat.idmaterifonemkalimat == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    # --- PRETEST & RANDOM FETCHING ---
    async def get_random_sentences(self, limit: int = 10):
        cat_query = select(Materifonemkalimat.kategori).distinct()
        categories = (await self.db.execute(cat_query)).scalars().all()
        
        results = []
        for cat in categories:
            if len(results) >= limit: break
            q = select(Materifonemkalimat).where(Materifonemkalimat.kategori == cat).order_by(func.random()).limit(1)
            item = (await self.db.execute(q)).scalar_one_or_none()
            if item: results.append(item)
            
        if len(results) < limit:
            needed = limit - len(results)
            exclude_ids = [r.idmaterifonemkalimat for r in results]
            q_more = select(Materifonemkalimat).where(Materifonemkalimat.idmaterifonemkalimat.notin_(exclude_ids)).order_by(func.random()).limit(needed)
            more_items = (await self.db.execute(q_more)).scalars().all()
            results.extend(more_items)
            
        return results

    async def get_random_word_by_phoneme(self, phoneme: str):
        query = select(Materifonemkata).where(Materifonemkata.fonem.ilike(f"%{phoneme}%")).order_by(func.random()).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_random_sentence_by_phoneme(self, phoneme: str):
        query = select(Materifonemkalimat).where(Materifonemkalimat.kategori.ilike(f"%{phoneme}%")).order_by(func.random()).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_word_by_id(self, id: int):
        return await self.db.get(Materifonemkata, id)

    async def get_sentence_by_id(self, id: int):
        return await self.db.get(Materifonemkalimat, id)
    
    # 1. Phoneme Material (Words)
    async def get_phoneme_materials_paginated(self, skip: int, limit: int, search: str = None):
        # Group by category, count words, get max updated_at
        stmt = select(
            Materifonemkata.kategori,
            func.count(Materifonemkata.idmaterifonemkata).label("total_words"),
            func.max(Materifonemkata.updated_at).label("last_update")
        ).group_by(Materifonemkata.kategori)
        
        count_stmt = select(func.count(distinct(Materifonemkata.kategori)))

        if search:
            stmt = stmt.where(Materifonemkata.kategori.ilike(f"%{search}%"))
            count_stmt = count_stmt.where(Materifonemkata.kategori.ilike(f"%{search}%"))
            
        total = await self.db.scalar(count_stmt) or 0
        
        stmt = stmt.order_by(Materifonemkata.kategori).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        
        return result.all(), total

    # 2. Exercise Phoneme (Sentences)
    async def get_exercise_materials_paginated(self, skip: int, limit: int, search: str = None):
        stmt = select(
            Materifonemkalimat.kategori,
            func.count(Materifonemkalimat.idmaterifonemkalimat).label("total_sentences"),
            func.max(Materifonemkalimat.updated_at).label("last_update")
        ).group_by(Materifonemkalimat.kategori)
        
        count_stmt = select(func.count(distinct(Materifonemkalimat.kategori)))

        if search:
            stmt = stmt.where(Materifonemkalimat.kategori.ilike(f"%{search}%"))
            count_stmt = count_stmt.where(Materifonemkalimat.kategori.ilike(f"%{search}%"))
            
        total = await self.db.scalar(count_stmt) or 0
        
        stmt = stmt.order_by(Materifonemkalimat.kategori).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        
        return result.all(), total

    # 3. Exam Phoneme
    async def get_exam_materials_paginated(self, skip: int, limit: int, search: str = None):
        stmt = select(
            Materiujian.kategori,
            func.count(Materiujian.idmateriujian).label("total_exams"),
            func.max(Materiujian.updated_at).label("last_update")
        ).group_by(Materiujian.kategori)
        
        count_stmt = select(func.count(distinct(Materiujian.kategori)))

        if search:
            stmt = stmt.where(Materiujian.kategori.ilike(f"%{search}%"))
            count_stmt = count_stmt.where(Materiujian.kategori.ilike(f"%{search}%"))
            
        total = await self.db.scalar(count_stmt) or 0
        
        stmt = stmt.order_by(Materiujian.kategori).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        
        return result.all(), total

    # --- INTERVIEW ---
    async def get_interview_questions(self, skip: int = 0, limit: int = 10):
        query = select(Materiinterview).order_by(Materiinterview.idmateriinterview).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_interview_question_by_id(self, id: int):
        return await self.db.get(Materiinterview, id)

    # --- ADMIN CRUD OPERATIONS ---
    async def create_word(self, data: dict):
        try:
            obj = Materifonemkata(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            return obj
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateError("Kata tersebut sudah ada dalam kategori ini")
            
    async def update_word(self, id: int, data: dict):
        from sqlalchemy import update
        stmt = update(Materifonemkata).where(Materifonemkata.idmaterifonemkata == id).values(**data)
        await self.db.execute(stmt)
        await self.db.commit()

    async def delete_word(self, id: int):
        from sqlalchemy import delete
        stmt = delete(Materifonemkata).where(Materifonemkata.idmaterifonemkata == id)
        await self.db.execute(stmt)
        await self.db.commit()

    async def create_sentence(self, data: dict):
        try:
            obj = Materifonemkalimat(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            return obj
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateError("Kalimat sudah ada")

    async def update_sentence(self, id: int, data: dict):
        from sqlalchemy import update
        stmt = update(Materifonemkalimat).where(Materifonemkalimat.idmaterifonemkalimat == id).values(**data)
        await self.db.execute(stmt)
        await self.db.commit()

    async def delete_sentence(self, id: int):
        from sqlalchemy import delete
        stmt = delete(Materifonemkalimat).where(Materifonemkalimat.idmaterifonemkalimat == id)
        await self.db.execute(stmt)
        await self.db.commit()

    async def create_exam_set(self, category: str, items: list):
        try:
            exam_header = Materiujian(kategori=category)
            self.db.add(exam_header)
            await self.db.flush()
            for item in items:
                detail = Materiujiankalimat(
                    idmateriujian=exam_header.idmateriujian,
                    kalimat=item["sentence"],
                    fonem=item["phoneme"]
                )
                self.db.add(detail)
            await self.db.commit()
            return exam_header
        except Exception as e:
            await self.db.rollback()
            raise e
            
    async def get_exam_header(self, id: int):
        return await self.db.get(Materiujian, id)
        
    async def delete_exam(self, id: int):
        from sqlalchemy import delete
        await self.db.execute(delete(Materiujiankalimat).where(Materiujiankalimat.idmateriujian == id))
        await self.db.execute(delete(Materiujian).where(Materiujian.idmateriujian == id))
        await self.db.commit()

    async def update_exam_sentences(self, exam_id: int, items: list):
        from sqlalchemy import update
        for item in items:
            stmt = update(Materiujiankalimat).where(Materiujiankalimat.idmateriujiankalimat == item["id_sentence"]).values(kalimat=item["sentence"], fonem=item["phoneme"])
            await self.db.execute(stmt)
        await self.db.commit()

    async def create_interview_question(self, question: str):
        obj = Materiinterview(question=question, is_active=True)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
        
    async def update_interview_question(self, id: int, question: str):
        obj = await self.get_interview_question_by_id(id)
        if obj:
            obj.question = question
            await self.db.commit()
            await self.db.refresh(obj)
        return obj

    async def delete_interview_question(self, id: int):
        from sqlalchemy import delete
        await self.db.execute(delete(Materiinterview).where(Materiinterview.idmateriinterview == id))
        await self.db.commit()
        
    async def toggle_interview_status(self, id: int):
        obj = await self.get_interview_question_by_id(id)
        if obj:
            obj.is_active = not obj.is_active
            await self.db.commit()
            await self.db.refresh(obj)
        return obj
        
    async def swap_interview_order(self, id: int, direction: str):
        current = await self.get_interview_question_by_id(id)
        if not current: return False
        
        target_q = None
        if direction == "up":
            q = select(Materiinterview).where(Materiinterview.idmateriinterview < id).order_by(Materiinterview.idmateriinterview.desc()).limit(1)
        else:
            q = select(Materiinterview).where(Materiinterview.idmateriinterview > id).order_by(Materiinterview.idmateriinterview.asc()).limit(1)
            
        target = (await self.db.execute(q)).scalar_one_or_none()
        
        if target:
            temp_q, temp_s = current.question, current.is_active
            current.question, current.is_active = target.question, target.is_active
            target.question, target.is_active = temp_q, temp_s
            await self.db.commit()
            return True
        return False
        
    async def get_all_word_categories(self):
        result = await self.db.execute(select(Materifonemkata.kategori).distinct())
        return result.scalars().all()
        
    async def get_all_sentence_categories(self):
        result = await self.db.execute(select(Materifonemkalimat.kategori).distinct())
        return result.scalars().all()
        
    async def get_words_by_category(self, category: str):
        result = await self.db.execute(select(Materifonemkata).where(Materifonemkata.kategori == category))
        return result.scalars().all()
        
    async def get_sentences_by_category(self, category: str):
        result = await self.db.execute(select(Materifonemkalimat).where(Materifonemkalimat.kategori == category))
        return result.scalars().all()