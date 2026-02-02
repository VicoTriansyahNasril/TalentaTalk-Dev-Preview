import pandas as pd
import io
from app.repositories.material_repository import MaterialRepository
from app.core.exceptions import AppError, NotFoundError

class MaterialService:
    def __init__(self, repo: MaterialRepository):
        self.repo = repo

    # --- EXCEL IMPORTS  ---
    def _validate_columns(self, df: pd.DataFrame, required: list):
        df.columns = df.columns.str.lower().str.strip()
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise AppError(status_code=400, detail=f"Missing columns: {', '.join(missing)}")
            
    async def import_words_from_excel(self, file_content: bytes):
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            self._validate_columns(df, ['kategori', 'kata', 'fonem', 'arti', 'definisi'])
            
            success, errors = 0, []
            for idx, row in df.iterrows():
                try:
                    data = {
                        "kategori": str(row['kategori']).strip(),
                        "kata": str(row['kata']).strip(),
                        "fonem": str(row['fonem']).strip(),
                        "meaning": str(row['arti']).strip(),
                        "definition": str(row['definisi']).strip()
                    }
                    await self.repo.create_word(data)
                    success += 1
                except Exception as e:
                    errors.append({"row": idx + 2, "error": str(e)})
            
            return {"successCount": success, "errorCount": len(errors), "errors": errors}
        except Exception as e:
            raise AppError(status_code=400, detail=f"Import failed: {str(e)}")

    async def import_sentences_from_excel(self, file_content: bytes):
        """Import Exercise Phoneme (Sentences)"""
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            self._validate_columns(df, ['kategori', 'kalimat', 'fonem'])
            
            success, errors = 0, []
            for idx, row in df.iterrows():
                try:
                    data = {
                        "phoneme_category": str(row['kategori']).strip(),
                        "sentence": str(row['kalimat']).strip(),
                        "phoneme": str(row['fonem']).strip()
                    }
                    # Validasi minimal length
                    if len(data['sentence'].split()) < 10:
                        raise ValueError("Sentence must have at least 10 words")
                    
                    await self.repo.create_sentence({
                        "kategori": data['phoneme_category'],
                        "kalimat": data['sentence'],
                        "fonem": data['phoneme']
                    })
                    success += 1
                except Exception as e:
                    errors.append({"row": idx + 2, "error": str(e)})
            
            return {"successCount": success, "errorCount": len(errors), "errors": errors}
        except Exception as e:
            raise AppError(status_code=400, detail=f"Import failed: {str(e)}")

    async def import_exams_from_excel(self, file_content: bytes):
        """Import Exam Phoneme (10 Sentences per Set)"""
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            # Validasi kolom kalimat_1 s/d 10 dan fonem_1 s/d 10
            req_cols = ['kategori'] + [f'kalimat_{i}' for i in range(1, 11)] + [f'fonem_{i}' for i in range(1, 11)]
            self._validate_columns(df, req_cols)
            
            success, errors = 0, []
            for idx, row in df.iterrows():
                try:
                    category = str(row['kategori']).strip()
                    if "-" not in category:
                         raise ValueError("Category must be a pair (e.g. i-I)")
                         
                    items = []
                    for i in range(1, 11):
                        sent = str(row[f'kalimat_{i}']).strip()
                        phon = str(row[f'fonem_{i}']).strip()
                        if not sent or not phon:
                            raise ValueError(f"Missing data at index {i}")
                        items.append({"sentence": sent, "phoneme": phon})
                    
                    await self.repo.create_exam_set(category, items)
                    success += 1
                except Exception as e:
                    errors.append({"row": idx + 2, "error": str(e)})
            
            return {"successCount": success, "errorCount": len(errors), "errors": errors}
        except Exception as e:
            raise AppError(status_code=400, detail=f"Import failed: {str(e)}")

    # --- WORD CRUD ---
    async def update_word(self, id: int, data: dict):
        word = await self.repo.get_word_by_id(id)
        if not word: raise NotFoundError("Word")
        await self.repo.update_word(id, data)

    async def delete_word(self, id: int):
        word = await self.repo.get_word_by_id(id)
        if not word: raise NotFoundError("Word")
        await self.repo.delete_word(id)

    # --- SENTENCE CRUD ---
    async def create_sentence(self, data: dict):
        if len(data['sentence'].split()) < 4: # Minimal 4 kata
             raise AppError(status_code=400, detail="Sentence too short")
        return await self.repo.create_sentence(data)

    async def update_sentence(self, id: int, data: dict):
        sent = await self.repo.get_sentence_by_id(id)
        if not sent: raise NotFoundError("Sentence")
        await self.repo.update_sentence(id, data)

    async def delete_sentence(self, id: int):
        sent = await self.repo.get_sentence_by_id(id)
        if not sent: raise NotFoundError("Sentence")
        await self.repo.delete_sentence(id)

    # --- EXAM CRUD ---
    async def delete_exam(self, id: int):
        exam = await self.repo.get_exam_header(id)
        if not exam: raise NotFoundError("Exam")
        await self.repo.delete_exam(id)

    async def update_exam_sentences(self, exam_id: int, items: list):
        # Validasi sederhana
        for item in items:
            if len(item.sentence.split()) < 10:
                raise AppError(status_code=400, detail="Exam sentence must be >= 10 words")
        
        items_dict = [item.model_dump() for item in items]
        await self.repo.update_exam_sentences(exam_id, items_dict)

    # --- INTERVIEW CRUD ---
    async def update_interview(self, id: int, question: str):
        q = await self.repo.get_interview_question_by_id(id)
        if not q: raise NotFoundError("Question")
        await self.repo.update_interview_question(id, question)

    async def delete_interview(self, id: int):
        q = await self.repo.get_interview_question_by_id(id)
        if not q: raise NotFoundError("Question")
        await self.repo.delete_interview_question(id)

    async def toggle_interview(self, id: int):
        q = await self.repo.get_interview_question_by_id(id)
        if not q: raise NotFoundError("Question")
        return await self.repo.toggle_interview_status(id)

    async def swap_interview(self, id: int, direction: str):
        success = await self.repo.swap_interview_order(id, direction)
        if not success:
            raise AppError(status_code=400, detail="Cannot move in that direction")