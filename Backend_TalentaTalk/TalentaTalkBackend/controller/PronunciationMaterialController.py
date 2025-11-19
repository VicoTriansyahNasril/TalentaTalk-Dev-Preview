# controller/PronunciationMaterialController.py

from typing import Optional, Dict, List, Any
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from sqlalchemy.exc import SQLAlchemyError
from psycopg2 import IntegrityError
import pandas as pd
import io
from utils.pagination import PaginationHelper
from utils.template_generator import ImportProcessor, TemplateGenerator
from config.phoneme_constants import PhonemeConstants, MaterialType

from models import (
    Materifonemkata, Materifonemkalimat, Materiinterview,
    Materiujian, Materiujiankalimat, Ujianfonem, Detailujianfonem
)


class PronunciationMaterialController:
    
    def __init__(self, db: Session):
        self.db = db

    # ... (fungsi-fungsi lain sebelum import_phoneme_exam_from_excel tidak berubah)
    def _validate_phoneme_transcription_for_word(self, phoneme_transcription: str, category: str) -> None:
        if not phoneme_transcription.strip():
            raise HTTPException(status_code=400, detail="Phoneme transcription cannot be empty")
        if category not in phoneme_transcription:
            raise HTTPException(status_code=400, detail=f"The phoneme transcription '{phoneme_transcription}' must contain the target category phoneme '{category}'. Example: category 'g' should be in transcription like 'gɛt'")
    
    def _validate_phoneme_transcription_for_sentence(self, phoneme_transcription: str, category: str) -> None:
        if not phoneme_transcription.strip():
            raise HTTPException(status_code=400, detail="Phoneme transcription cannot be empty")
        if "-" not in category:
            raise HTTPException(status_code=400, detail=f"Category for sentence materials must be similar phonemes (e.g., 'i-ɪ', 'p-b', 'ə-ʌ-ɚ'), got: '{category}'")
        try:
            phonemes = [p.strip() for p in category.split("-") if p.strip()]
            if len(phonemes) < 2:
                raise ValueError("Need at least 2 phonemes")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid similar phonemes format: '{category}'. Use format like 'i-ɪ', 'p-b', or 'ə-ʌ-ɚ'")
        for phoneme in phonemes:
            if not PhonemeConstants.is_valid_phoneme(phoneme):
                raise HTTPException(status_code=400, detail=f"Invalid phoneme '{phoneme}' in category '{category}'")
        missing_phonemes = [p for p in phonemes if p not in phoneme_transcription]
        if missing_phonemes:
            raise HTTPException(status_code=400, detail=f"The phoneme transcription '{phoneme_transcription}' must contain ALL phonemes from the category '{category}'. Missing: {', '.join(missing_phonemes)}. This is essential for similar phonemes training.")
    
    def _validate_category_phoneme(self, category: str, material_type: str = "word") -> None:
        if not category.strip():
            raise HTTPException(status_code=400, detail="Phoneme category cannot be empty")
        if material_type == "word":
            if not PhonemeConstants.is_valid_phoneme(category):
                valid_phonemes = ', '.join(PhonemeConstants.get_all_phonemes()[:10]) + '...'
                raise HTTPException(status_code=400, detail=f"Invalid phoneme category: '{category}'. Must be a single phoneme like: {valid_phonemes}")
        elif material_type in ["sentence", "exam"]:
            if "-" not in category:
                raise HTTPException(status_code=400, detail=f"Category for {material_type} materials must be similar phonemes (e.g., 'i-ɪ', 'p-b', 'ə-ʌ-ɚ')")
            phonemes = [p.strip() for p in category.split("-") if p.strip()]
            if len(phonemes) < 2:
                raise HTTPException(status_code=400, detail=f"Category for {material_type} materials must have at least 2 similar phonemes")
            for phoneme in phonemes:
                if not PhonemeConstants.is_valid_phoneme(phoneme):
                    raise HTTPException(status_code=400, detail=f"Invalid phoneme '{phoneme}' in category '{category}'")
            self._validate_phonemes_are_similar(phonemes, category)

    def _validate_phonemes_are_similar(self, phonemes: List[str], category: str) -> None:
        if len(phonemes) < 2:
            return
        first_phoneme = phonemes[0]
        related_phonemes = {first_phoneme}
        similar_to_first = PhonemeConstants.get_similar_phonemes(first_phoneme)
        related_phonemes.update(similar_to_first)
        for similar_phoneme in similar_to_first:
            additional_similar = PhonemeConstants.get_similar_phonemes(similar_phoneme)
            related_phonemes.update(additional_similar)
        category_phonemes = set(phonemes)
        unrelated_phonemes = category_phonemes - related_phonemes
        if unrelated_phonemes:
            similar_options = PhonemeConstants.get_similar_phonemes(first_phoneme)
            suggestion = f"Try using: {first_phoneme}-{'-'.join(similar_options[:2])}" if similar_options else f"'{first_phoneme}' may not have documented similar phonemes"
            raise HTTPException(status_code=400, detail=f"Phonemes {list(unrelated_phonemes)} in category '{category}' are not similar to '{first_phoneme}' according to phoneme similarity rules. {suggestion}")
        
    def _validate_uploaded_file(self, file: UploadFile) -> None:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        if not file.filename.lower().endswith(('.xlsx', '.csv')):
            raise HTTPException(status_code=400, detail="Only .xlsx and .csv files are supported")
        if file.size == 0:
            raise HTTPException(status_code=400, detail="File cannot be empty")
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must not exceed 10MB")

    def _read_uploaded_file(self, file: UploadFile) -> pd.DataFrame:
        try:
            contents = file.file.read()
            df = pd.read_excel(io.BytesIO(contents)) if file.filename.lower().endswith('.xlsx') else pd.read_csv(io.BytesIO(contents))
            df.columns = df.columns.str.strip()
            df = df.dropna(how='all')
            return df
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
        finally:
            file.file.seek(0)

    def get_phoneme_materials(self, search: Optional[str] = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        page, size = PaginationHelper.validate_pagination_params(page, size)
        query = self.db.query(Materifonemkata).distinct(Materifonemkata.kategori)
        if search and search.strip():
            query = query.filter(Materifonemkata.kategori.ilike(f"%{search.strip()}%"))
        categories = query.all()
        total_items = len(categories)
        paginated_categories = categories[(page - 1) * size : page * size]
        result = []
        for material in paginated_categories:
            total_word_count = self.db.query(Materifonemkata).filter(Materifonemkata.kategori == material.kategori).count()
            sample_words = self.db.query(Materifonemkata.kata).filter(Materifonemkata.kategori == material.kategori).limit(3).all()
            words_list = [w.kata for w in sample_words]
            words_string = ", ".join(words_list)
            if total_word_count > 3:
                words_string += "..."
            result.append({"phoneme": material.kategori, "words": words_string, "totalWords": total_word_count, "last_update": material.updated_at.strftime("%d/%m/%Y") if hasattr(material, 'updated_at') and material.updated_at else "20/6/2025"})
        return PaginationHelper.create_paginated_response(data=result, total_items=total_items, page=page, size=size)

    def add_phoneme_word(self, phoneme_category: str, word: str, meaning: str, word_definition: str, phoneme: str) -> Dict[str, Any]:
        self._validate_category_phoneme(phoneme_category, "word")
        self._validate_phoneme_transcription_for_word(phoneme, phoneme_category)
        if self.db.query(Materifonemkata).filter(Materifonemkata.kategori == phoneme_category, Materifonemkata.kata == word).first():
            raise HTTPException(status_code=400, detail="Material with this word in category already exists")
        new_material = Materifonemkata(kategori=phoneme_category, kata=word, meaning=meaning, definition=word_definition, fonem=phoneme)
        self.db.add(new_material)
        self.db.commit()
        self.db.refresh(new_material)
        return {"message": "Material added successfully", "data": {"id": new_material.idmaterifonemkata, "category": new_material.kategori, "word": new_material.kata, "meaning": new_material.meaning, "definition": new_material.definition, "phoneme": new_material.fonem}}

    def import_phoneme_word_from_excel(self, file: UploadFile) -> Dict[str, Any]:
        try:
            self._validate_uploaded_file(file)
            df = self._read_uploaded_file(file)
            validation_result = TemplateGenerator.validate_import_file(df, MaterialType.WORD)
            if not validation_result["is_valid"]:
                raise HTTPException(status_code=400, detail=f"File validation failed: {'; '.join(validation_result['errors'])}")
            
            process_result = ImportProcessor.process_phoneme_words(df)
            success_count, error_count, errors = 0, 0, []
            
            for word_data in process_result["processed_data"]:
                try:
                    if self.db.query(Materifonemkata).filter(Materifonemkata.kategori == word_data["kategori"], Materifonemkata.kata == word_data["kata"]).first():
                        errors.append({"row": f"Word: {word_data['kata']}", "reason": f"Word '{word_data['kata']}' already exists in category '{word_data['kategori']}'"})
                        error_count += 1
                        continue
                    new_material = Materifonemkata(kategori=word_data["kategori"], kata=word_data["kata"], meaning=word_data["meaning"], definition=word_data["definition"], fonem=word_data["fonem"])
                    self.db.add(new_material)
                    success_count += 1
                except Exception as e:
                    errors.append({"row": f"Word: {word_data.get('kata', 'unknown')}", "reason": f"Database error: {str(e)}"})
                    error_count += 1
            
            if success_count > 0:
                self.db.commit()
            
            all_errors = process_result["errors"] + errors
            total_error_count = process_result["error_count"] + error_count
            
            return {"message": f"{success_count} phoneme words imported successfully", "success_count": success_count, "error_count": total_error_count, "skipped": all_errors, "total_processed": success_count + total_error_count}
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

    def update_phoneme_word(self, word_id: int, payload: Dict[str, Any]) -> Dict[str, str]:
        material = self.db.query(Materifonemkata).filter(Materifonemkata.idmaterifonemkata == word_id).first()
        if not material:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")
        if "kategori" in payload:
            new_category = payload["kategori"].strip()
            self._validate_category_phoneme(new_category, "word")
            material.kategori = new_category
        if "kata" in payload:
            material.kata = payload["kata"].strip()
        if "meaning" in payload:
            material.meaning = payload["meaning"].strip()
        if "definition" in payload:
            material.definition = payload["definition"].strip()
        if "fonem" in payload:
            phoneme_transcription = payload["fonem"].strip()
            current_category = payload.get("kategori", material.kategori)
            self._validate_phoneme_transcription_for_word(phoneme_transcription, current_category)
            material.fonem = phoneme_transcription
        self.db.commit()
        return {"message": "Data berhasil diperbarui"}

    def delete_phoneme_word(self, word_id: int) -> Dict[str, str]:
        material = self.db.query(Materifonemkata).filter(Materifonemkata.idmaterifonemkata == word_id).first()
        if not material:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")
        try:
            self.db.delete(material)
            self.db.commit()
            return {"message": "Data berhasil dihapus"}
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def get_phoneme_words_by_category(self, kategori: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
        page, size = PaginationHelper.validate_pagination_params(page, size)
        query = self.db.query(Materifonemkata).filter(Materifonemkata.kategori == kategori)
        total_data = query.count()
        materials = query.order_by(Materifonemkata.kata.asc()).offset((page - 1) * size).limit(size).all()
        results = [{"id": item.idmaterifonemkata, "word": item.kata, "meaning": item.meaning, "definition": item.definition, "phoneme": item.fonem, "category": item.kategori} for item in materials]
        return PaginationHelper.create_paginated_response(data=results, total_items=total_data, page=page, size=size, additional_data={"category": kategori})

    def get_exercise_phoneme(self, search: Optional[str] = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        page, size = PaginationHelper.validate_pagination_params(page, size)
        query = self.db.query(Materifonemkalimat).distinct(Materifonemkalimat.kategori)
        if search and search.strip():
            query = query.filter(Materifonemkalimat.kategori.ilike(f"%{search.strip()}%"))
        categories = query.all()
        total_items = len(categories)
        paginated_categories = categories[(page - 1) * size : page * size]
        result = []
        for material in paginated_categories:
            total_sentence_count = self.db.query(Materifonemkalimat).filter(Materifonemkalimat.kategori == material.kategori).count()
            result.append({"phoneme_category": material.kategori, "totalSentence": total_sentence_count, "last_update": material.updated_at.strftime("%d/%m/%Y") if hasattr(material, 'updated_at') and material.updated_at else "20/6/2025"})
        return PaginationHelper.create_paginated_response(data=result, total_items=total_items, page=page, size=size)

    def add_phoneme_sentence(self, phoneme_category: str, sentence: str, phoneme: str) -> Dict[str, Any]:
        self._validate_category_phoneme(phoneme_category, "sentence")
        self._validate_phoneme_transcription_for_sentence(phoneme, phoneme_category)
        if self.db.query(Materifonemkalimat).filter(Materifonemkalimat.kategori == phoneme_category, Materifonemkalimat.kalimat == sentence).first():
            raise HTTPException(status_code=409, detail="This exact sentence already exists in this category.")
        new_material = Materifonemkalimat(kategori=phoneme_category, kalimat=sentence, fonem=phoneme)
        try:
            self.db.add(new_material)
            self.db.commit()
            self.db.refresh(new_material)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error occurred while adding the sentence.")
        return {"message": "Sentence material added successfully", "data": {"id": new_material.idmaterifonemkalimat, "category": new_material.kategori, "sentence": new_material.kalimat, "phoneme": new_material.fonem}}

    def import_phoneme_sentence_from_excel(self, file: UploadFile) -> Dict[str, Any]:
        try:
            self._validate_uploaded_file(file)
            df = self._read_uploaded_file(file)
            
            required_cols = ["kategori", "kalimat", "fonem"]
            if not all(col in df.columns for col in required_cols):
                raise HTTPException(status_code=400, detail=f"File must contain columns: {', '.join(required_cols)}")

            success_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    kategori = str(row['kategori']).strip()
                    kalimat = str(row['kalimat']).strip()
                    fonem = str(row['fonem']).strip()
                    
                    if not all([kategori, kalimat, fonem]):
                        raise ValueError("All fields (kategori, kalimat, fonem) are required.")
                    
                    self._validate_category_phoneme(kategori, "sentence")
                    self._validate_phoneme_transcription_for_sentence(fonem, kategori)
                    
                    if len(kalimat.split()) < 10:
                        raise ValueError("Sentence must contain at least 10 words.")

                    if self.db.query(Materifonemkalimat).filter_by(kategori=kategori, kalimat=kalimat).first():
                        raise ValueError(f"Sentence already exists in category '{kategori}'.")

                    new_material = Materifonemkalimat(kategori=kategori, kalimat=kalimat, fonem=fonem)
                    self.db.add(new_material)
                    success_count += 1
                
                except (ValueError, HTTPException) as e:
                    errors.append({"row": index + 2, "reason": str(e.detail if isinstance(e, HTTPException) else e)})
                except Exception as e:
                    errors.append({"row": index + 2, "reason": f"An unexpected error occurred: {str(e)}"})

            if success_count > 0:
                self.db.commit()
            else:
                self.db.rollback()

            return {
                "total_processed": len(df),
                "success_count": success_count,
                "error_count": len(errors),
                "skipped": errors
            }
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Import failed due to an unexpected error: {str(e)}")

    def update_phoneme_sentence(self, sentence_id: int, payload: Dict[str, Any]) -> Dict[str, str]:
        material = self.db.query(Materifonemkalimat).filter(Materifonemkalimat.idmaterifonemkalimat == sentence_id).first()
        if not material:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")
        if "kategori" in payload:
            kategori = payload["kategori"].strip()
            self._validate_category_phoneme(kategori, "sentence")
            material.kategori = kategori
        if "kalimat" in payload:
            material.kalimat = payload["kalimat"].strip()
        if "fonem" in payload:
            fonem = payload["fonem"].strip()
            current_category = payload.get("kategori", material.kategori)
            self._validate_phoneme_transcription_for_sentence(fonem, current_category)
            material.fonem = fonem
        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            if "duplicate key value violates unique constraint" in str(e):
                raise HTTPException(status_code=400, detail="Kalimat dengan kategori ini sudah ada")
            raise HTTPException(status_code=500, detail="Terjadi kesalahan database")
        return {"message": "Data berhasil diperbarui"}

    def delete_phoneme_sentence(self, sentence_id: int) -> Dict[str, str]:
        material = self.db.query(Materifonemkalimat).filter(Materifonemkalimat.idmaterifonemkalimat == sentence_id).first()
        if not material:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")
        try:
            self.db.delete(material)
            self.db.commit()
            return {"message": "Data berhasil dihapus"}
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def get_phoneme_sentences_by_category(self, kategori: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
        page, size = PaginationHelper.validate_pagination_params(page, size)
        query = self.db.query(Materifonemkalimat).filter(Materifonemkalimat.kategori == kategori)
        total_data = query.count()
        materials = query.order_by(Materifonemkalimat.kalimat.asc()).offset((page - 1) * size).limit(size).all()
        results = [{"id": item.idmaterifonemkalimat, "sentence": item.kalimat, "phoneme": item.fonem} for item in materials]
        return PaginationHelper.create_paginated_response(data=results, total_items=total_data, page=page, size=size, additional_data={"category": kategori})

    def get_exam_phoneme(self, search: Optional[str] = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        page, size = PaginationHelper.validate_pagination_params(page, size)
        query = self.db.query(Materiujian).distinct(Materiujian.kategori)
        if search and search.strip():
            query = query.filter(Materiujian.kategori.ilike(f"%{search.strip()}%"))
        categories = query.all()
        total_items = len(categories)
        paginated_categories = categories[(page - 1) * size : page * size]
        result = []
        for material in paginated_categories:
            total_exam_count = self.db.query(Materiujian).filter(Materiujian.kategori == material.kategori).count()
            result.append({"phoneme_category": material.kategori, "totalExam": total_exam_count, "last_update": material.updated_at.strftime("%d/%m/%Y") if hasattr(material, 'updated_at') and material.updated_at else "20/6/2025"})
        return PaginationHelper.create_paginated_response(data=result, total_items=total_items, page=page, size=size)

    def add_phoneme_exam(self, category: str, sentences_and_phonemes: List[Dict[str, str]]) -> Dict[str, Any]:
        self._validate_category_phoneme(category, "exam")
        if len(sentences_and_phonemes) != 10:
            raise HTTPException(status_code=400, detail="Each exam must have exactly 10 sentences.")
        for i, pair in enumerate(sentences_and_phonemes, 1):
            phoneme_transcription = pair["phoneme"]
            try:
                self._validate_phoneme_transcription_for_sentence(phoneme_transcription, category)
            except HTTPException as e:
                raise HTTPException(status_code=400, detail=f"Sentence {i}: {e.detail}")
        
        new_exam = Materiujian(kategori=category)
        self.db.add(new_exam)
        self.db.commit()
        self.db.refresh(new_exam)
        exam_id = new_exam.idmateriujian
        
        for pair in sentences_and_phonemes:
            kalimat = Materiujiankalimat(idmateriujian=exam_id, kalimat=pair["sentence"], fonem=pair["phoneme"])
            self.db.add(kalimat)
        self.db.commit()
        return {"message": "Exam added successfully", "data": {"category": category, "total_sentences": len(sentences_and_phonemes)}}

    def import_phoneme_exam_from_excel(self, file: UploadFile) -> Dict[str, Any]:
        try:
            self._validate_uploaded_file(file)
            df = self._read_uploaded_file(file)
            
            # Validasi kolom dasar
            required_cols = ["kategori"]
            if not all(col in df.columns for col in required_cols):
                raise HTTPException(status_code=400, detail=f"File must contain column: {', '.join(required_cols)}")

            # Validasi kolom kalimat dan fonem (harus ada 10 pasang)
            for i in range(1, 11):
                if f"kalimat_{i}" not in df.columns or f"fonem_{i}" not in df.columns:
                    raise HTTPException(status_code=400, detail=f"Missing column 'kalimat_{i}' or 'fonem_{i}'. Template must contain 10 sentence and 10 phoneme columns.")

            success_count = 0
            errors = []
            successful_exams_info = []

            for index, row in df.iterrows():
                try:
                    category = str(row['kategori']).strip()
                    self._validate_category_phoneme(category, "exam")
                    
                    sentences_and_phonemes = []
                    for i in range(1, 11):
                        sentence = str(row[f'kalimat_{i}']).strip()
                        phoneme = str(row[f'fonem_{i}']).strip()

                        if not sentence or not phoneme:
                            raise ValueError(f"Sentence and phoneme for item {i} cannot be empty.")
                        
                        if len(sentence.split()) < 10:
                             raise ValueError(f"Sentence {i} must have at least 10 words.")

                        self._validate_phoneme_transcription_for_sentence(phoneme, category)
                        sentences_and_phonemes.append({"sentence": sentence, "phoneme": phoneme})
                    
                    # Jika semua validasi lolos, tambahkan ke DB
                    new_exam = Materiujian(kategori=category)
                    self.db.add(new_exam)
                    self.db.flush() # Mendapatkan ID sebelum commit penuh
                    
                    for pair in sentences_and_phonemes:
                        kalimat = Materiujiankalimat(idmateriujian=new_exam.idmateriujian, kalimat=pair["sentence"], fonem=pair["phoneme"])
                        self.db.add(kalimat)
                    
                    successful_exams_info.append({
                        "exam_id": new_exam.idmateriujian,
                        "category": category,
                        "sentences_count": len(sentences_and_phonemes)
                    })
                    success_count += 1
                
                except (ValueError, HTTPException) as e:
                    errors.append({"row": index + 2, "reason": str(e.detail if isinstance(e, HTTPException) else e)})
                except Exception as e:
                    errors.append({"row": index + 2, "reason": f"An unexpected error occurred: {str(e)}"})
            
            if success_count > 0:
                self.db.commit()
            else:
                self.db.rollback()

            return {
                "total_processed": len(df),
                "success_count": success_count,
                "error_count": len(errors),
                "errors": errors,
                "successful_exams": successful_exams_info
            }

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Import failed due to an unexpected error: {str(e)}")


    def delete_phoneme_exam(self, exam_id: int) -> Dict[str, str]:
        """Menghapus exam set beserta semua data terkaitnya."""
        exam = self.db.query(Materiujian).filter(Materiujian.idmateriujian == exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")

        try:
            ujian_fonem_records = self.db.query(Ujianfonem).filter(Ujianfonem.idmateriujian == exam_id).all()
            ujian_fonem_ids = [record.idujian for record in ujian_fonem_records]

            if ujian_fonem_ids:
                self.db.query(Detailujianfonem).filter(Detailujianfonem.idujian.in_(ujian_fonem_ids)).delete(synchronize_session=False)
                self.db.query(Ujianfonem).filter(Ujianfonem.idujian.in_(ujian_fonem_ids)).delete(synchronize_session=False)

            self.db.query(Materiujiankalimat).filter(Materiujiankalimat.idmateriujian == exam_id).delete(synchronize_session=False)
            self.db.delete(exam)
            self.db.commit()
            return {"message": "Exam set and all related data deleted successfully"}

        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error during deletion: {str(e)}")

    def get_exam_detail_by_category(self, category: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        page, per_page = PaginationHelper.validate_pagination_params(page, per_page)
        exams_query = self.db.query(Materiujian).filter(Materiujian.kategori == category).order_by(Materiujian.idmateriujian.asc())
        total_items = exams_query.count()
        if total_items == 0:
            return {"category": category, "exams": [], "current_page": page, "total_pages": 0, "total_items": 0}
        exams = exams_query.offset((page - 1) * per_page).limit(per_page).all()
        result = []
        for idx, exam in enumerate(exams, start=1 + (page - 1) * per_page):
            sentence_count = self.db.query(Materiujiankalimat).filter(Materiujiankalimat.idmateriujian == exam.idmateriujian).count()
            result.append({"exam_id": exam.idmateriujian, "test_number": f"Test {idx}", "total_sentence": sentence_count, "last_update": exam.updated_at.strftime("%Y-%m-%d %H:%M:%S") if exam.updated_at else None})
        total_pages = (total_items + per_page - 1) // per_page
        return {"category": category, "exams": result, "current_page": page, "total_pages": total_pages, "total_items": total_items}

    def get_exam_detail_by_id(self, idmateriujian: int) -> Dict[str, Any]:
        materi = self.db.query(Materiujian).filter_by(idmateriujian=idmateriujian).first()
        if not materi:
            raise HTTPException(status_code=404, detail="Exam not found")
        kalimat_list = self.db.query(Materiujiankalimat).filter_by(idmateriujian=idmateriujian).all()
        return {"id_exam": materi.idmateriujian, "phoneme_category": materi.kategori, "sentences": [{"id_sentence": k.idmateriujiankalimat, "sentence": k.kalimat, "phoneme": k.fonem} for k in kalimat_list]}

    def update_exam_detail(self, idmateriujian: int, sentences_data: List[Dict[str, Any]]) -> Dict[str, str]:
        for s in sentences_data:
            kalimat_obj = self.db.query(Materiujiankalimat).filter_by(idmateriujiankalimat=s["id_sentence"], idmateriujian=idmateriujian).first()
            if kalimat_obj:
                kalimat_obj.kalimat = s["sentence"]
                kalimat_obj.fonem = s["phoneme"]
            else:
                raise HTTPException(status_code=404, detail=f"Sentence ID {s['id_sentence']} not found in this exam")
        self.db.commit()
        return {"message": "Exam sentences updated successfully"}

    def get_interview_questions(self, search: Optional[str] = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        page, size = PaginationHelper.validate_pagination_params(page, size)
        query = self.db.query(Materiinterview)
        if search and search.strip():
            query = query.filter(Materiinterview.question.ilike(f"%{search.strip()}%"))
        total_items = query.count()
        offset = (page - 1) * size
        questions = query.order_by(Materiinterview.idmateriinterview.asc()).offset(offset).limit(size).all()
        result = []
        for idx, question in enumerate(questions):
            overall_position = ((page - 1) * size) + idx + 1
            result.append({"questionId": f"QST{question.idmateriinterview:03d}", "interviewQuestion": question.question, "createdAt": question.updated_at.strftime("%Y-%m-%d %H:%M:%S") if question.updated_at else "2025-06-20 00:00:00", "orderPosition": overall_position, "dbId": question.idmateriinterview, "isActive": question.is_active})
        pagination = {"currentPage": page, "pageSize": size, "totalRecords": total_items, "totalPages": (total_items + size - 1) // size if total_items > 0 else 1, "hasNextPage": page < ((total_items + size - 1) // size if total_items > 0 else 1), "hasPreviousPage": page > 1}
        return {"interviewQuestions": result, "pagination": pagination}
    
    def swap_question_order(self, question_id: int, direction: str) -> Dict[str, Any]:
        if direction not in ["up", "down"]:
            raise HTTPException(status_code=400, detail="Direction must be 'up' or 'down'")
        current_question = self.db.query(Materiinterview).filter(Materiinterview.idmateriinterview == question_id).first()
        if not current_question:
            raise HTTPException(status_code=404, detail="Question not found")
        if direction == "up":
            adjacent_question = self.db.query(Materiinterview).filter(Materiinterview.idmateriinterview < question_id).order_by(Materiinterview.idmateriinterview.desc()).first()
            if not adjacent_question:
                raise HTTPException(status_code=400, detail="Question is already at the top")
        else:
            adjacent_question = self.db.query(Materiinterview).filter(Materiinterview.idmateriinterview > question_id).order_by(Materiinterview.idmateriinterview.asc()).first()
            if not adjacent_question:
                raise HTTPException(status_code=400, detail="Question is already at the bottom")
        temp_question, temp_updated_at = current_question.question, current_question.updated_at
        current_question.question, current_question.updated_at = adjacent_question.question, adjacent_question.updated_at
        adjacent_question.question, adjacent_question.updated_at = temp_question, temp_updated_at
        self.db.commit()
        return {"message": f"Question moved {direction} successfully", "data": {"movedQuestionId": question_id, "swappedWithId": adjacent_question.idmateriinterview, "direction": direction}}
    
    def reorder_all_questions(self, question_ids_order: List[int]) -> Dict[str, Any]:
        questions_data = []
        for question_id in question_ids_order:
            question = self.db.query(Materiinterview).filter(Materiinterview.idmateriinterview == question_id).first()
            if question:
                questions_data.append({"id": question.idmateriinterview, "question": question.question, "updated_at": question.updated_at})
        for idx, new_data in enumerate(questions_data):
            target_id = question_ids_order[idx]
            target_question = self.db.query(Materiinterview).filter(Materiinterview.idmateriinterview == target_id).first()
            if target_question:
                target_question.question = new_data["question"]
                target_question.updated_at = new_data["updated_at"]
        self.db.commit()
        return {"message": "Questions reordered successfully", "data": {"newOrder": question_ids_order}}
    
    def get_questions_for_mobile(self, limit: Optional[int] = None) -> Dict[str, Any]:
        query = self.db.query(Materiinterview).filter(Materiinterview.is_active == True).order_by(Materiinterview.idmateriinterview.asc())
        if limit:
            query = query.limit(limit)
        questions = query.all()
        result = [{"id": question.idmateriinterview, "question": question.question, "order": idx, "questionId": f"QST{question.idmateriinterview:03d}"} for idx, question in enumerate(questions, 1)]
        return {"questions": result, "total": len(result), "message": "Questions ordered for mobile delivery"}

    def add_interview_material(self, interview_question: str) -> Dict[str, Any]:
        if self.db.query(Materiinterview).filter(Materiinterview.question == interview_question).first():
            raise HTTPException(status_code=400, detail="Interview question already exists")
        new_question = Materiinterview(question=interview_question, is_active=True)
        self.db.add(new_question)
        self.db.commit()
        self.db.refresh(new_question)
        return {"message": "Interview question added successfully", "data": {"id": new_question.idmateriinterview, "interview_question": new_question.question, "updated_at": new_question.updated_at}}

    def update_interview_question(self, question_id: int, interview_question: str) -> Dict[str, str]:
        question = self.db.query(Materiinterview).filter(Materiinterview.idmateriinterview == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Interview question not found")
        question.question = interview_question.strip()
        try:
            self.db.commit()
            self.db.refresh(question)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        return {"message": "Interview question updated successfully"}
        
    def toggle_interview_question_status(self, question_id: int) -> Dict[str, Any]:
        question = self.db.query(Materiinterview).filter(Materiinterview.idmateriinterview == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Interview question not found")
        question.is_active = not question.is_active
        self.db.commit()
        self.db.refresh(question)
        return {"message": "Question status updated successfully", "data": {"questionId": question.idmateriinterview, "isActive": question.is_active}}

    def delete_interview_question(self, question_id: int) -> Dict[str, str]:
        question = self.db.query(Materiinterview).filter(Materiinterview.idmateriinterview == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Interview question not found")
        try:
            self.db.delete(question)
            self.db.commit()
            return {"message": "Interview question deleted successfully"}
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def get_interview_question_by_id(self, question_id: int) -> Dict[str, Any]:
        question = self.db.query(Materiinterview).filter(Materiinterview.idmateriinterview == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Interview question not found")
        return {"id": question.idmateriinterview, "interview_question": question.question, "updated_at": question.updated_at}