# controller/TalentController.py

import io
from typing import Dict, List, Any, Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc
import pandas as pd
from datetime import datetime

from controller.AuthController import hash_password
from utils.pagination import PaginationHelper
from utils.timestamp_helper import TimestampHelper
from utils.interview_feedback_parser import InterviewFeedbackParser
from models import (
    Talent, Materifonemkata, Materifonemkalimat, Materiujian, Materiujiankalimat,
    Hasillatihanfonem, Hasillatihanpercakapan, Hasillatihaninterview,
    Ujianfonem, Detailujianfonem, Materipercakapan
)
from sqlalchemy.dialects import postgresql
import logging

class TalentController:
    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # HELPER METHODS
    # ==========================================

    def _validate_talent_exists(self, talent_id: int) -> Talent:
        """Validasi apakah talent ada dan mengembalikannya."""
        talent = self.db.query(Talent).filter(Talent.idtalent == talent_id).first()
        if not talent:
            raise HTTPException(status_code=404, detail="Talent not found")
        return talent

    def _get_talent_info(self, talent: Talent) -> Dict[str, Any]:
        latest_exam = self.db.query(Ujianfonem).filter(
            Ujianfonem.idtalent == talent.idtalent
        ).order_by(desc(Ujianfonem.waktuujian)).first()

        highest_exam_score = self.db.query(func.max(Ujianfonem.nilai)).filter(
            Ujianfonem.idtalent == talent.idtalent
        ).scalar()

        total_soal_fonem = self.db.query(func.count(Materifonemkata.idmaterifonemkata)).scalar() + self.db.query(func.count(Materifonemkalimat.idmaterifonemkalimat)).scalar()
        unique_soal_dikerjakan = self.db.query(func.count(func.distinct(Hasillatihanfonem.idsoal))).filter(
            Hasillatihanfonem.idtalent == talent.idtalent
        ).scalar()
        completion_percent = (unique_soal_dikerjakan / total_soal_fonem * 100) if total_soal_fonem > 0 else 0
        
        return {
            "talentId": f"TLT{talent.idtalent:03d}",
            "nama": talent.nama,
            "role": talent.role or "Talent",
            "email": talent.email,
            "lastExam": f"{latest_exam.nilai:.0f}%" if latest_exam and latest_exam.nilai is not None else "N/A",
            "highestExam": f"{highest_exam_score:.0f}%" if highest_exam_score is not None else "N/A",
            "progress": f"{completion_percent:.0f}%"
        }

    # ==========================================
    # TALENT MANAGEMENT (CRUD)
    # ==========================================

    def get_talent_list(self, search: Optional[str], page: int, size: int) -> Dict[str, Any]:
        """GET /web/admin/talents - Mengambil daftar talent."""
        page, size = PaginationHelper.validate_pagination_params(page, size)
        
        query = self.db.query(Talent)
        if search and search.strip():
            query = query.filter(or_(
                Talent.nama.ilike(f"%{search.strip()}%"),
                Talent.email.ilike(f"%{search.strip()}%")
            ))

        total_items = query.count()
        talents = query.order_by(Talent.idtalent.asc()).offset((page - 1) * size).limit(size).all()
        
        result_data = [self._process_talent_data_for_list(t) for t in talents]

        return PaginationHelper.create_paginated_response(result_data, total_items, page, size, "talents")

    def _process_talent_data_for_list(self, talent: Talent) -> Dict[str, Any]:
        """Memproses data talent tunggal untuk halaman list."""
        pretest_score = talent.pretest_score

        highest_exam_score = self.db.query(func.max(Ujianfonem.nilai)).filter(
            Ujianfonem.idtalent == talent.idtalent
        ).scalar()
        
        total_soal_fonem = self.db.query(func.count(Materifonemkata.idmaterifonemkata)).scalar() + self.db.query(func.count(Materifonemkalimat.idmaterifonemkalimat)).scalar()
        unique_soal_dikerjakan = self.db.query(func.count(func.distinct(Hasillatihanfonem.idsoal))).filter(
            Hasillatihanfonem.idtalent == talent.idtalent
        ).scalar()
        
        completion_percent = (unique_soal_dikerjakan / total_soal_fonem * 100) if total_soal_fonem > 0 else 0

        return {
            "id": talent.idtalent,
            "talentName": talent.nama,
            "email": talent.email,
            "role": talent.role,
            "pretest": f"{pretest_score:.0f}%" if pretest_score is not None else "N/A",
            "highestExam": f"{highest_exam_score:.0f}%" if highest_exam_score is not None else "N/A",
            "progress": f"{completion_percent:.0f}%"
        }

    def get_talent_by_id(self, talent_id: int) -> Dict[str, Any]:
        """Mengambil data talent tunggal berdasarkan ID."""
        talent = self._validate_talent_exists(talent_id)
        return self._get_talent_info(talent)

    def add_talent(self, nama: str, email: str, role: str = "talent", password: str = "default123") -> Dict[str, Any]:
        existing = self.db.query(Talent).filter(Talent.email == email).first()
        if existing: raise HTTPException(status_code=409, detail="Email sudah terdaftar")
        new_talent = Talent(nama=nama, email=email, password=hash_password(password), role=role or "Talent")
        self.db.add(new_talent)
        self.db.commit(); self.db.refresh(new_talent)
        
        talent_data = {
            "id": new_talent.idtalent,
            "nama": new_talent.nama,
            "email": new_talent.email,
            "role": new_talent.role
        }
        return {"data": talent_data}

    def update_talent(self, id_talent: int, nama: Optional[str], email: Optional[str], role: Optional[str]) -> Dict[str, Any]:
        talent = self._validate_talent_exists(id_talent)
        if nama is not None: talent.nama = nama
        if email is not None: talent.email = email
        if role is not None: talent.role = role
        self.db.commit()
        self.db.refresh(talent)
        
        updated_data = {
            "id": talent.idtalent,
            "nama": talent.nama,
            "email": talent.email,
            "role": talent.role
        }
        return {"data": updated_data}

    def change_talent_password(self, id_talent: int, new_password: str) -> Dict[str, str]:
        talent = self._validate_talent_exists(id_talent)
        talent.password = hash_password(new_password)
        self.db.commit()
        return {"message": "Password berhasil diubah"}

    def delete_talent(self, id_talent: int):
        talent = self._validate_talent_exists(id_talent)
        self.db.query(Hasillatihanfonem).filter(Hasillatihanfonem.idtalent == id_talent).delete()
        self.db.query(Hasillatihanpercakapan).filter(Hasillatihanpercakapan.idtalent == id_talent).delete()
        self.db.query(Hasillatihaninterview).filter(Hasillatihaninterview.idtalent == id_talent).delete()
        ujian_ids = self.db.query(Ujianfonem.idujian).filter(Ujianfonem.idtalent == id_talent)
        self.db.query(Detailujianfonem).filter(Detailujianfonem.idujian.in_(ujian_ids)).delete(synchronize_session=False)
        self.db.query(Ujianfonem).filter(Ujianfonem.idtalent == id_talent).delete()
        self.db.delete(talent)
        self.db.commit()

    def import_talents_from_excel(self, file: UploadFile) -> Dict[str, Any]:

        try:

            if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
                raise HTTPException(
                    status_code=400, 
                    detail="Format file tidak didukung. Gunakan file Excel (.xlsx, .xls) atau CSV (.csv)"
                )

            if file.size and file.size > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail="Ukuran file terlalu besar. Maksimal 10MB"
                )

            try:
                contents = file.file.read()
                buffer = io.BytesIO(contents)
                if file.filename.lower().endswith('.csv'):
                    df = pd.read_csv(buffer, encoding='utf-8')
                else:
                    df = pd.read_excel(buffer)
            except Exception as read_error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Gagal membaca file: {str(read_error)}. Pastikan file tidak rusak dan dalam format yang benar."
                )

            df.columns = df.columns.str.strip()
            df = df.dropna(how='all')

            if df.empty:
                raise HTTPException(
                    status_code=400,
                    detail="File kosong atau tidak ada data yang dapat diproses"
                )

            required_columns = ["nama", "email", "role", "password"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Template tidak valid. Kolom yang hilang: {', '.join(missing_columns)}. Pastikan menggunakan template yang benar."
                )

            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    nama = str(row['nama']).strip() if pd.notna(row['nama']) else ""
                    email = str(row['email']).strip() if pd.notna(row['email']) else ""
                    role = str(row['role']).strip() if pd.notna(row['role']) else ""
                    password = str(row['password']).strip() if pd.notna(row['password']) else ""

                    if not all([nama, email, role, password]):
                        raise ValueError("Semua kolom wajib diisi.")

                    if '@' not in email or '.' not in email:
                        raise ValueError(f"Format email tidak valid: {email}")
                    
                    if len(password) < 6:
                        raise ValueError("Password harus minimal 6 karakter.")

                    if self.db.query(Talent).filter(Talent.email == email).first():
                        raise ValueError(f"Email '{email}' sudah terdaftar.")

                    new_talent = Talent(
                        nama=nama,
                        email=email,
                        role=role,
                        password=hash_password(password)
                    )
                    self.db.add(new_talent)
                    success_count += 1

                except ValueError as ve:
                    error_count += 1
                    errors.append({"row": index + 2, "error": str(ve)})
                except Exception as e:
                    error_count += 1
                    errors.append({"row": index + 2, "error": f"Kesalahan tidak terduga: {str(e)}"})

            if success_count > 0:
                try:
                    self.db.commit()
                except Exception as commit_error:
                    self.db.rollback()
                    raise HTTPException(
                        status_code=500,
                        detail=f"Gagal menyimpan data ke database: {str(commit_error)}"
                    )
            else:
                self.db.rollback()

            return {
                "totalProcessed": len(df),
                "successCount": success_count,
                "errorCount": error_count,
                "errors": errors
            }
            
        except HTTPException:
            raise 
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Gagal memproses file: {str(e)}"
            )
            
    # =====================
    # TALENT DETAIL VIEWS
    # =====================

    def get_phoneme_material_exercise_progress(self, talent_id: int, page: int, limit: int) -> Dict[str, Any]:
        talent = self._validate_talent_exists(talent_id)
        
        all_categories_q = self.db.query(Materifonemkata.kategori).distinct().subquery()
        
        talent_stats_q = self.db.query(
            Materifonemkata.kategori,
            func.count(func.distinct(Hasillatihanfonem.idsoal)).label('attempted_words'),
            func.avg(Hasillatihanfonem.nilai).label('avg_accuracy'),
            func.max(Hasillatihanfonem.waktulatihan).label('last_activity')
        ).join(Materifonemkata, and_(
            Materifonemkata.idmaterifonemkata == Hasillatihanfonem.idsoal,
            Hasillatihanfonem.typelatihan == 'Word'
        )).filter(Hasillatihanfonem.idtalent == talent_id).group_by(Materifonemkata.kategori).subquery()
        
        base_query = self.db.query(
            all_categories_q.c.kategori.label('phoneme_category'),
            func.count(Materifonemkata.idmaterifonemkata).label('total_words'),
            func.coalesce(talent_stats_q.c.attempted_words, 0).label('attempted'),
            func.coalesce(talent_stats_q.c.avg_accuracy, 0).label('accuracy'),
            talent_stats_q.c.last_activity
        ).join(Materifonemkata, Materifonemkata.kategori == all_categories_q.c.kategori)\
        .outerjoin(talent_stats_q, talent_stats_q.c.kategori == all_categories_q.c.kategori)\
        .group_by(all_categories_q.c.kategori, talent_stats_q.c.attempted_words, talent_stats_q.c.avg_accuracy, talent_stats_q.c.last_activity)

        total_items = base_query.count()
        results = base_query.order_by(
            desc(talent_stats_q.c.last_activity).nulls_last(), 
            all_categories_q.c.kategori
        ).offset((page - 1) * limit).limit(limit).all()

        categories_data = [{
            "phonemeCategory": cat.phoneme_category,
            "wordsAttempted": f"{cat.attempted}/{cat.total_words}",
            "averageAccuracy": f"{cat.accuracy:.0f}%"
        } for cat in results]
        
        response = PaginationHelper.create_paginated_response(categories_data, total_items, page, limit, "phonemeCategories")
        response["talentInfo"] = self._get_talent_info(talent)
        return response

    def get_phoneme_word_detail(self, talent_id: int, phoneme_category: str, page: int, limit: int) -> Dict[str, Any]:
        talent = self._validate_talent_exists(talent_id)
        
        latest_attempt_subq = self.db.query(
            Hasillatihanfonem.idsoal,
            func.max(Hasillatihanfonem.waktulatihan).label('latest_attempt')
        ).filter(
            Hasillatihanfonem.idtalent == talent_id,
            Hasillatihanfonem.typelatihan == 'Word'
        ).group_by(Hasillatihanfonem.idsoal).subquery()

        base_query = self.db.query(Materifonemkata).filter(Materifonemkata.kategori == phoneme_category)
        total_items = base_query.count()

        words_material_query = base_query.outerjoin(
            latest_attempt_subq, Materifonemkata.idmaterifonemkata == latest_attempt_subq.c.idsoal
        ).order_by(asc(latest_attempt_subq.c.latest_attempt).nulls_first(), Materifonemkata.idmaterifonemkata.asc())
        
        words_material = words_material_query.offset((page - 1) * limit).limit(limit).all()

        words_data = []
        for word in words_material:
            stats = self.db.query(
                func.max(Hasillatihanfonem.waktulatihan),
                func.max(Hasillatihanfonem.nilai),
                (self.db.query(Hasillatihanfonem.nilai).filter(and_(Hasillatihanfonem.idsoal == word.idmaterifonemkata, Hasillatihanfonem.idtalent == talent_id)).order_by(desc(Hasillatihanfonem.waktulatihan)).limit(1).scalar_subquery())
            ).filter(and_(
                Hasillatihanfonem.idsoal == word.idmaterifonemkata,
                Hasillatihanfonem.idtalent == talent_id,
                Hasillatihanfonem.typelatihan == 'Word'
            )).first()
            
            words_data.append({
                "word": word.kata,
                "latestAttempted": TimestampHelper.format_timestamp(stats[0]) or "N/A",
                "bestScore": f"{stats[1] or 0:.0f}%",
                "latestScore": f"{stats[2] or 0:.0f}%"
            })

        response = PaginationHelper.create_paginated_response(words_data, total_items, page, limit, "words")
        response_data = {"phonemeDetail": {"category": phoneme_category, "words": response['words']}, "pagination": response['pagination']}
        response_data["talentInfo"] = self._get_talent_info(talent)
        return response_data

    def get_phoneme_exercise_progress(self, talent_id: int, page: int, limit: int) -> Dict[str, Any]:
        talent = self._validate_talent_exists(talent_id)
        
        all_categories_q = self.db.query(Materifonemkalimat.kategori).distinct().subquery()
        
        talent_stats_q = self.db.query(
            Materifonemkalimat.kategori,
            func.count(func.distinct(Hasillatihanfonem.idsoal)).label('attempted'),
            func.avg(Hasillatihanfonem.nilai).label('accuracy'),
            func.max(Hasillatihanfonem.waktulatihan).label('last_activity')
        ).join(Materifonemkalimat, and_(
            Materifonemkalimat.idmaterifonemkalimat == Hasillatihanfonem.idsoal,
            Hasillatihanfonem.typelatihan == 'Sentence'
        )).filter(Hasillatihanfonem.idtalent == talent_id).group_by(Materifonemkalimat.kategori).subquery()
        
        base_query = self.db.query(
            all_categories_q.c.kategori.label('phoneme_category'),
            func.count(Materifonemkalimat.idmaterifonemkalimat).label('total'),
            func.coalesce(talent_stats_q.c.attempted, 0).label('attempted'),
            func.coalesce(talent_stats_q.c.accuracy, 0).label('accuracy'),
            talent_stats_q.c.last_activity
        ).join(Materifonemkalimat, Materifonemkalimat.kategori == all_categories_q.c.kategori)\
        .outerjoin(talent_stats_q, talent_stats_q.c.kategori == all_categories_q.c.kategori)\
        .group_by(all_categories_q.c.kategori, talent_stats_q.c.attempted, talent_stats_q.c.accuracy, talent_stats_q.c.last_activity)

        total_items = base_query.count()
        results = base_query.order_by(
            desc(talent_stats_q.c.last_activity).nulls_last(), 
            all_categories_q.c.kategori
        ).offset((page - 1) * limit).limit(limit).all()

        exercises_data = []
        for ex in results:
            exercises_data.append({
                "phonemeCategory": ex.phoneme_category,
                "sentenceAttempted": f"{ex.attempted}/{ex.total}",
                "averageAccuracy": f"{ex.accuracy:.0f}%",
            })
            
        response = PaginationHelper.create_paginated_response(exercises_data, total_items, page, limit, "phonemeExercises")
        response["talentInfo"] = self._get_talent_info(talent)
        return response
    
    def get_phoneme_exercise_detail(self, talent_id: int, phoneme_category: str, page: int, limit: int) -> Dict[str, Any]:
        talent = self._validate_talent_exists(talent_id)
        
        latest_attempt_subq = self.db.query(
            Hasillatihanfonem.idsoal,
            func.max(Hasillatihanfonem.waktulatihan).label('latest_attempt')
        ).filter(
            Hasillatihanfonem.idtalent == talent_id,
            Hasillatihanfonem.typelatihan == 'Sentence'
        ).group_by(Hasillatihanfonem.idsoal).subquery()

        base_query = self.db.query(Materifonemkalimat).filter(Materifonemkalimat.kategori == phoneme_category)
        total_items = base_query.count()
        
        sentences_material_query = base_query.outerjoin(
            latest_attempt_subq, Materifonemkalimat.idmaterifonemkalimat == latest_attempt_subq.c.idsoal
        ).order_by(asc(latest_attempt_subq.c.latest_attempt).nulls_first(), Materifonemkalimat.idmaterifonemkalimat.asc())
        
        sentences_material = sentences_material_query.offset((page - 1) * limit).limit(limit).all()
        
        sentences_data = []
        for sentence in sentences_material:
            stats = self.db.query(
                func.max(Hasillatihanfonem.waktulatihan),
                func.max(Hasillatihanfonem.nilai),
                (self.db.query(Hasillatihanfonem.nilai).filter(and_(Hasillatihanfonem.idsoal == sentence.idmaterifonemkalimat, Hasillatihanfonem.idtalent == talent_id)).order_by(desc(Hasillatihanfonem.waktulatihan)).limit(1).scalar_subquery())
            ).filter(and_(
                Hasillatihanfonem.idsoal == sentence.idmaterifonemkalimat,
                Hasillatihanfonem.idtalent == talent_id,
                Hasillatihanfonem.typelatihan == 'Sentence'
            )).first()
            
            sentences_data.append({
                "sentence": sentence.kalimat,
                "latestAttempted": TimestampHelper.format_timestamp(stats[0]) or "N/A",
                "bestScore": f"{stats[1] or 0:.0f}%",
                "latestScore": f"{stats[2] or 0:.0f}%"
            })

        response = PaginationHelper.create_paginated_response(sentences_data, total_items, page, limit, "sentences")
        response_data = {"phonemeDetail": {"category": phoneme_category, "sentences": response['sentences']}, "pagination": response['pagination']}
        response_data["talentInfo"] = self._get_talent_info(talent)
        return response_data

    def get_phoneme_exam_progress(self, talent_id: int, page: int, limit: int) -> Dict[str, Any]:
        talent = self._validate_talent_exists(talent_id)
        
        base_query = self.db.query(
            Ujianfonem.kategori,
            func.max(Ujianfonem.nilai).label('best_score'),
            (self.db.query(Ujianfonem.nilai).filter(
                Ujianfonem.kategori == Ujianfonem.kategori,
                Ujianfonem.idtalent == talent_id
            ).order_by(desc(Ujianfonem.waktuujian)).limit(1).scalar_subquery()).label('latest_score'),
            func.max(Ujianfonem.waktuujian).label('last_activity')
        ).filter(Ujianfonem.idtalent == talent_id).group_by(Ujianfonem.kategori)

        total_items = base_query.count()
        exams = base_query.order_by(
            desc('last_activity').nulls_last(), 
            Ujianfonem.kategori
        ).offset((page - 1) * limit).limit(limit).all()
        
        exams_data = [{
            "phonemeCategory": ex.kategori,
            "bestScore": f"{ex.best_score or 0:.0f}%",
            "latestScore": f"{ex.latest_score or 0:.0f}%"
        } for ex in exams]

        response = PaginationHelper.create_paginated_response(exams_data, total_items, page, limit, "phonemeExams")
        response["talentInfo"] = self._get_talent_info(talent)
        return response

    def get_phoneme_exam_detail(self, talent_id: int, phoneme_category: str, page: int, limit: int) -> Dict[str, Any]:
        talent = self._validate_talent_exists(talent_id)
        
        base_query = self.db.query(Ujianfonem).filter(
            Ujianfonem.idtalent == talent_id,
            Ujianfonem.kategori == phoneme_category
        ).order_by(desc(Ujianfonem.waktuujian))

        total_items = base_query.count()
        exams = base_query.offset((page - 1) * limit).limit(limit).all()
        
        exam_totals_data = []
        for i, exam in enumerate(exams):
            exam_totals_data.append({
                "examName": f"Exam {total_items - ((page - 1) * limit) - i}",
                "examId": exam.idujian,
                "score": f"{exam.nilai or 0:.0f}%",
                "date": TimestampHelper.format_timestamp(exam.waktuujian)
            })

        response = PaginationHelper.create_paginated_response(exam_totals_data, total_items, page, limit, "examTotals")
        response_data = {"examDetail": {"category": phoneme_category, "examTotals": response['examTotals']}, "pagination": response['pagination']}
        response_data["talentInfo"] = self._get_talent_info(talent)
        return response_data
    
    def get_phoneme_exam_attempt_detail(self, talent_id: int, attempt_id: int) -> Dict[str, Any]:
        talent = self._validate_talent_exists(talent_id)
        
        exam_attempt = self.db.query(Ujianfonem).filter(
            Ujianfonem.idtalent == talent_id,
            Ujianfonem.idujian == attempt_id
        ).first()

        if not exam_attempt:
            raise HTTPException(status_code=404, detail="Exam attempt not found for this talent")
        exam_details_query = self.db.query(
            Detailujianfonem.nilai,
            Materiujiankalimat.kalimat,
            Materiujiankalimat.fonem
        ).join(
            Materiujiankalimat, Detailujianfonem.idsoal == Materiujiankalimat.idmateriujiankalimat
        ).filter(
            Detailujianfonem.idujian == attempt_id
        ).order_by(Materiujiankalimat.idmateriujiankalimat.asc())

        exam_details = exam_details_query.all()

        sentences_data = []
        for score, sentence_text, phoneme_transcription in exam_details:
            sentences_data.append({
                "sentence": sentence_text,
                "phonemeTranscription": phoneme_transcription,
                "score": f"{score or 0:.0f}%"
            })

        response_data = {
            "talentInfo": self._get_talent_info(talent),
            "examAttemptDetail": {
                "attemptId": f"ATT{exam_attempt.idujian:03d}",
                "phonemeCategory": exam_attempt.kategori,
                "totalScore": f"{exam_attempt.nilai or 0:.0f}%",
                "date": TimestampHelper.format_timestamp(exam_attempt.waktuujian),
                "sentences": sentences_data
            }
        }
        
        return response_data

    def get_conversation_progress(self, talent_id: int, page: int, limit: int) -> Dict[str, Any]:
        """Get conversation progress with fixed wpm field"""
        talent = self._validate_talent_exists(talent_id)
        
        base_query = self.db.query(Hasillatihanpercakapan, Materipercakapan.topic).join(
            Materipercakapan
        ).filter(
            Hasillatihanpercakapan.idtalent == talent_id
        ).order_by(desc(Hasillatihanpercakapan.waktulatihan))
        
        total_items = base_query.count()
        attempts_db = base_query.offset((page - 1) * limit).limit(limit).all()

        attempts_data = []
        for att in attempts_db:
            attempts_data.append({
                "topic": att.topic or "General",
                "wpm": f"{att.Hasillatihanpercakapan.wpm or 0:.0f}",
                "grammarIssue": att.Hasillatihanpercakapan.grammar or "No issues",
                "date": TimestampHelper.format_timestamp(att.Hasillatihanpercakapan.waktulatihan)
            })
        
        response = PaginationHelper.create_paginated_response(attempts_data, total_items, page, limit, "conversations")
        response["talentInfo"] = self._get_talent_info(talent)
        return response
    
    def get_interview_progress(self, talent_id: int, page: int, limit: int) -> Dict[str, Any]:
        """Get interview progress with fixed wpm field"""
        talent = self._validate_talent_exists(talent_id)
        
        base_query = self.db.query(Hasillatihaninterview).filter(
            Hasillatihaninterview.idtalent == talent_id
        ).order_by(desc(Hasillatihaninterview.waktulatihan))
        
        total_items = base_query.count()
        attempts_db = base_query.offset((page - 1) * limit).limit(limit).all()

        attempts_data = []
        for i, attempt in enumerate(attempts_db):
            attempts_data.append({
                "attempt": total_items - ((page - 1) * limit) - i,
                "attemptId": attempt.idhasilinterview,
                "wordProducePerMinute": f"{attempt.wpm or 0:.0f}",
                "feedback": attempt.feedback or "No feedback",
                "date": TimestampHelper.format_timestamp(attempt.waktulatihan)
            })
            
        response = PaginationHelper.create_paginated_response(attempts_data, total_items, page, limit, "interviews")
        response["talentInfo"] = self._get_talent_info(talent)
        return response

    def get_interview_attempt_detail(self, talent_id: int, attempt_id: int) -> Dict[str, Any]:
        """Get detailed interview attempt information with parsed feedback"""
        talent = self._validate_talent_exists(talent_id)
        interview = self.db.query(Hasillatihaninterview).filter(
            Hasillatihaninterview.idhasilinterview == attempt_id,
            Hasillatihaninterview.idtalent == talent_id
        ).first()

        if not interview:
            raise HTTPException(status_code=404, detail="Interview attempt not found")
        
        parsed_feedback = InterviewFeedbackParser.parse_feedback_to_components(interview.feedback or "")
        
        total_attempts = self.db.query(func.count(Hasillatihaninterview.idhasilinterview)).filter(
            Hasillatihaninterview.idtalent == talent_id
        ).scalar()
        
        attempt_rank_query = self.db.query(Hasillatihaninterview.idhasilinterview).filter(
            Hasillatihaninterview.idtalent == talent_id
        ).order_by(desc(Hasillatihaninterview.waktulatihan)).all()
        
        try:
            current_attempt_index = [item[0] for item in attempt_rank_query].index(attempt_id)
            attempt_number = total_attempts - current_attempt_index
        except ValueError:
            attempt_number = 1

        return {
            "talentInfo": self._get_talent_info(talent),
            "interviewDetail": {
                "attemptNumber": attempt_number,
                "date": TimestampHelper.format_timestamp(interview.waktulatihan),
                "feedback": {
                    "strength": parsed_feedback.get("strength", "Not available"),
                    "weakness": parsed_feedback.get("weakness", "Not available"),
                    "performance": parsed_feedback.get("performance", "Not available"),
                    "wpm": f"{interview.wpm or 0:.0f}",
                    "grammar": interview.grammar or "Not evaluated"
                }
            }
        }