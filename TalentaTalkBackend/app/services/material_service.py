import pandas as pd
import io
from app.repositories.material_repository import MaterialRepository
from app.core.exceptions import AppError, NotFoundError

class MaterialService:
    def __init__(self, repo: MaterialRepository):
        self.repo = repo

    def _validate_columns(self, df: pd.DataFrame, required: list):
        df.columns = df.columns.str.lower().str.strip()
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise AppError(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

    def _validate_phoneme_content(self, phoneme: str, category: str, text: str):
        """Strict validation ensuring phonemes match category"""
        if "-" in category:
            target_phonemes = category.split("-")
            for p in target_phonemes:
                if p not in phoneme:
                    raise AppError(status_code=400, detail=f"Phoneme transcription must contain all targets from category '{category}'. Missing: {p}")
        else:
            if category not in phoneme:
                raise AppError(status_code=400, detail=f"Phoneme transcription must contain target '{category}'")

    async def import_words_from_excel(self, file_content: bytes):
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            self._validate_columns(df, ['kategori', 'kata', 'fonem', 'arti', 'definisi'])
            
            success, errors = 0, []
            for idx, row in df.iterrows():
                try:
                    cat = str(row['kategori']).strip()
                    word = str(row['kata']).strip()
                    phon = str(row['fonem']).strip()
                    
                    self._validate_phoneme_content(phon, cat, word)
                    
                    data = {
                        "kategori": cat, "kata": word, "fonem": phon,
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
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            self._validate_columns(df, ['kategori', 'kalimat', 'fonem'])
            
            success, errors = 0, []
            for idx, row in df.iterrows():
                try:
                    cat = str(row['kategori']).strip()
                    sent = str(row['kalimat']).strip()
                    phon = str(row['fonem']).strip()
                    
                    if len(sent.split()) < 4:
                        raise ValueError("Sentence must have at least 4 words")
                    
                    self._validate_phoneme_content(phon, cat, sent)
                    
                    await self.repo.create_sentence({
                        "kategori": cat, "kalimat": sent, "fonem": phon
                    })
                    success += 1
                except Exception as e:
                    errors.append({"row": idx + 2, "error": str(e)})
            
            return {"successCount": success, "errorCount": len(errors), "errors": errors}
        except Exception as e:
            raise AppError(status_code=400, detail=f"Import failed: {str(e)}")

    async def import_exams_from_excel(self, file_content: bytes):
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            req_cols = ['kategori'] + [f'kalimat_{i}' for i in range(1, 11)] + [f'fonem_{i}' for i in range(1, 11)]
            self._validate_columns(df, req_cols)
            
            success, errors = 0, []
            for idx, row in df.iterrows():
                try:
                    category = str(row['kategori']).strip()
                    if "-" not in category:
                         raise ValueError("Exam category must be a pair (e.g. i-I)")
                         
                    items = []
                    for i in range(1, 11):
                        sent = str(row[f'kalimat_{i}']).strip()
                        phon = str(row[f'fonem_{i}']).strip()
                        if not sent or not phon:
                            raise ValueError(f"Missing data at index {i}")
                        
                        self._validate_phoneme_content(phon, category, sent)
                        items.append({"sentence": sent, "phoneme": phon})
                    
                    await self.repo.create_exam_set(category, items)
                    success += 1
                except Exception as e:
                    errors.append({"row": idx + 2, "error": str(e)})
            
            return {"successCount": success, "errorCount": len(errors), "errors": errors}
        except Exception as e:
            raise AppError(status_code=400, detail=f"Import failed: {str(e)}")

    async def update_word(self, id: int, data: dict):
        word = await self.repo.get_word_by_id(id)
        if not word: raise NotFoundError("Word")
        await self.repo.update_word(id, data)

    async def delete_word(self, id: int):
        word = await self.repo.get_word_by_id(id)
        if not word: raise NotFoundError("Word")
        await self.repo.delete_word(id)

    async def create_sentence(self, data: dict):
        if len(data['sentence'].split()) < 4:
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

    async def delete_exam(self, id: int):
        exam = await self.repo.get_exam_header(id)
        if not exam: raise NotFoundError("Exam")
        await self.repo.delete_exam(id)

    async def update_exam_sentences(self, exam_id: int, items: list):
        for item in items:
            if len(item.sentence.split()) < 4:
                raise AppError(status_code=400, detail="Exam sentence must be >= 4 words")
        items_dict = [item.model_dump() for item in items]
        await self.repo.update_exam_sentences(exam_id, items_dict)

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