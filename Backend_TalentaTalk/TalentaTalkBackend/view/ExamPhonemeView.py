# view/ExamPhonemeView.py
from fastapi import APIRouter, Depends, Query, Body, Path, File, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List

from models import Materiujiankalimat
from controller.AuthController import get_current_admin_user
from controller.PronunciationMaterialController import PronunciationMaterialController
from database import get_db
from utils.timestamp_helper import TimestampHelper
from utils.response_formatter import APIResponse
from utils.template_generator import TemplateGenerator
from schemas import AddExamSentenceRequest, UpdateSentenceRequest
from config.phoneme_constants import MaterialType

examphonemematerialrouter = APIRouter(
    prefix="/web/admin",
    dependencies=[Depends(get_current_admin_user)]
)

# ... (kode lain sebelum add_exam_bulk_sentences tidak berubah)
@examphonemematerialrouter.get("/exam-phoneme")
def get_exam_phoneme(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10),
    sortBy: Optional[str] = Query(None),
    sortOrder: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Exam Phoneme Management"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.get_exam_phoneme(search, page, limit)
        
        if not result.get("data"):
            response_data = {
                "examPhonemes": [],
                "pagination": {
                    "currentPage": page,
                    "totalPages": 0,
                    "totalRecords": 0,
                    "showing": "No exam data available"
                }
            }
            return APIResponse.success(
                data=response_data,
                message="Belum ada exam phoneme"
            )
        
        exam_phonemes = []
        for exam in result["data"]:
            exam_phonemes.append({
                "phonemeCategory": exam["phoneme_category"],
                "totalExam": exam["total_exam"],
                "lastUpdate": exam["last_update"]
            })
        
        response_data = {
            "examPhonemes": exam_phonemes,
            "pagination": result.get("pagination", {})
        }
        
        return APIResponse.success(
            data=response_data,
            message="Data exam phoneme berhasil diambil"
        )
        
    except Exception as e:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@examphonemematerialrouter.post("/exam-phoneme/bulk-sentences")
def add_exam_bulk_sentences(
    request: AddExamSentenceRequest,
    db: Session = Depends(get_db)
):
    """Add New Exam Sentence Modal - 10 sentences at once"""
    try:
        controller = PronunciationMaterialController(db)
        
        # Membaca data dari 'request.items' sesuai skema AddExamSentenceRequest
        sentences_and_phonemes = [
            {"sentence": item.sentence, "phoneme": item.phoneme}
            for item in request.items
        ]
        
        # Menggunakan 'request.category' sesuai skema
        result = controller.add_phoneme_exam(request.category, sentences_and_phonemes)
        
        sentences_data = [
            {"sentenceId": f"SEN{100 + i:03d}", "sentence": item.sentence}
            for i, item in enumerate(request.items, 1)
        ]
        
        response_data = {
            "examId": f"EXM{100:03d}",
            "phonemeCategory": request.category,
            "totalSentencesAdded": len(request.items),
            "sentences": sentences_data,
            "createdAt": TimestampHelper.get_current_timestamp()
        }
        
        return APIResponse.success(
            data=response_data,
            message=f"Exam phoneme berhasil dibuat dengan {len(request.items)} sentences",
            status_code=status.HTTP_201_CREATED
        )
        
    except HTTPException as e:
        # Penanganan error tetap sama
        if "minimal pair" in str(e.detail) or "exactly 10 sentences" in str(e.detail) or "must be one of" in str(e.detail):
            return APIResponse.error(message=str(e.detail), status_code=status.HTTP_400_BAD_REQUEST)
        raise e
    except Exception as e:
        return APIResponse.error(message="Terjadi kesalahan server", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ... (sisa kode di file ini tidak berubah)
@examphonemematerialrouter.get("/exam-phoneme/import-template")
def get_exam_phoneme_template():
    """Get import template untuk exam phoneme - MENGEMBALIKAN FILE EXCEL"""
    try:
        template_data = TemplateGenerator.get_template_by_type(MaterialType.EXAM)
        buffer = TemplateGenerator.create_excel_buffer(template_data)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=\"exam_phoneme_template.xlsx\""}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat template: {str(e)}")

@examphonemematerialrouter.post("/exam-phoneme/import")
def import_exam_phoneme(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Exercise Exam Modal - ENHANCED VERSION"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.import_phoneme_exam_from_excel(file)
        
        # Extract data from result
        successful_exams = result.get('successful_exams', [])
        errors = result.get('errors', [])
        
        success_count = len(successful_exams)
        error_count = len(errors)
        total_processed = success_count + error_count
        
        response_data = {
            "totalProcessed": total_processed,
            "successCount": success_count,
            "errorCount": error_count,
            "errors": [
                {
                    "row": error.get("category", error.get("row", "unknown")),
                    "error": error.get("reason", str(error))
                } for error in errors
            ],
            "successfulExams": [
                {
                    "examId": f"EXM{exam['exam_id']:03d}",
                    "category": exam["category"],
                    "sentencesCount": exam["sentences_count"]
                } for exam in successful_exams
            ]
        }
        
        if success_count > 0:
            message = f"Import berhasil: {success_count} exam set ditambahkan"
            if error_count > 0:
                message += f", {error_count} error"
        else:
            message = f"Import gagal: {error_count} error ditemukan"
        
        return APIResponse.success(
            data=response_data,
            message=message
        )
        
    except HTTPException as e:
        if "Template harus memiliki kolom" in str(e.detail):
            return APIResponse.error(
                message="Template harus memiliki kolom Sentence 1 sampai Sentence 10",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return APIResponse.error(
            message=str(e.detail),
            status_code=e.status_code
        )
    except Exception as e:
        return APIResponse.error(
            message="Terjadi kesalahan saat import file",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@examphonemematerialrouter.delete("/exam-phoneme/{phoneme_category}/tests/{test_id}")
def delete_exam_test(
    phoneme_category: str,
    test_id: str,
    db: Session = Depends(get_db)
):
    """Delete exam test"""
    try:
        try:
            exam_numeric_id = int(test_id.replace("TST", ""))
        except ValueError:
            exam_numeric_id = int(test_id)
        
        controller = PronunciationMaterialController(db)
        result = controller.delete_phoneme_exam(exam_numeric_id)
        
        response_data = {
            "testId": test_id,
            "deletedAt": TimestampHelper.get_current_timestamp()
        }
        
        return APIResponse.success(
            data=response_data,
            message="Test exam berhasil dihapus"
        )
        
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            return APIResponse.error(
                message="Test exam tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        raise e
    except Exception as e:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@examphonemematerialrouter.get("/exam-phoneme/{phoneme_category}/tests/{test_id}/sentences")
def get_exam_sentences_detail(
    phoneme_category: str,
    test_id: str,
    db: Session = Depends(get_db)
):
    """Detail Exam Phoneme Sentences Modal"""
    try:
        try:
            exam_numeric_id = int(test_id.replace("TST", ""))
        except ValueError:
            exam_numeric_id = int(test_id)
        
        controller = PronunciationMaterialController(db)
        result = controller.get_exam_detail_by_id(exam_numeric_id)
        
        sentences_data = []
        for idx, sentence_obj in enumerate(result.get("sentences", []), 1):
            sentences_data.append({
                "sentenceId": f"SEN{sentence_obj['id_sentence']:03d}",
                "id_sentence": sentence_obj['id_sentence'],
                "sentenceOrder": idx,
                "sentence": sentence_obj["sentence"],
                "phoneme": sentence_obj.get("phoneme", "")
            })
        
        total_sentences = len(sentences_data)
        is_complete = total_sentences == 10
        
        response_data = {
            "testInfo": {
                "testId": test_id,
                "phonemeCategory": phoneme_category,
                "testTo": 1
            },
            "sentences": sentences_data,
            "totalSentences": total_sentences,
            "isComplete": is_complete
        }
        
        message = "Detail exam sentences berhasil diambil"
        if not is_complete:
            response_data["warning"] = "Exam ini tidak lengkap, harus ada 10 sentences"
            message = "Data exam tidak lengkap"
        
        return APIResponse.success(
            data=response_data,
            message=message
        )
        
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            return APIResponse.error(
                message="Test exam tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        raise e
    except Exception as e:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@examphonemematerialrouter.put("/exam-phoneme/sentences/{sentence_id}")
def update_exam_sentence(
    sentence_id: int,
    request: UpdateSentenceRequest,
    db: Session = Depends(get_db)
):
    """Edit Individual Exam Sentence - ENHANCED VERSION"""
    try:
        controller = PronunciationMaterialController(db)
        
        # Get the actual exam for this sentence
        sentence_obj = controller.db.query(Materiujiankalimat).filter(
            Materiujiankalimat.idmateriujiankalimat == sentence_id
        ).first()
        
        if not sentence_obj:
            return APIResponse.error(
                message="Sentence tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        actual_exam_id = sentence_obj.idmateriujian
        
        # Prepare update data for single sentence
        update_data = [{
            "id_sentence": request.id_sentence,
            "sentence": request.sentence,
            "phoneme": request.phoneme
        }]

        # Use the existing update_exam_detail method
        result = controller.update_exam_detail(actual_exam_id, update_data)
        
        response_data = {
            "sentenceId": f"SEN{sentence_id:03d}",
            "sentence": request.sentence,
            "phoneme": request.phoneme,
            "updatedAt": TimestampHelper.get_current_timestamp()
        }
        
        return APIResponse.success(
            data=response_data,
            message="Exam sentence berhasil diperbarui"
        )
        
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            return APIResponse.error(
                message="Exam sentence tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        elif "validation" in str(e.detail).lower():
            return APIResponse.error(
                message=str(e.detail),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        raise e
    except Exception as e:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@examphonemematerialrouter.put("/exam-phoneme/{phoneme_category}/tests/{test_id}")
def update_full_exam(
    phoneme_category: str,
    test_id: str,
    request: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Update Full Exam Set - All 10 sentences - ENHANCED VERSION"""
    try:
        # Parse test_id
        try:
            exam_numeric_id = int(test_id.replace("TST", ""))
        except ValueError:
            exam_numeric_id = int(test_id)
        
        controller = PronunciationMaterialController(db)
        
        # Validate request data
        if "sentences" not in request or len(request["sentences"]) != 10:
            return APIResponse.error(
                message="Exam must have exactly 10 sentences",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare update data with enhanced validation
        sentences_data = []
        for i, sentence_data in enumerate(request["sentences"]):
            if not sentence_data.get("sentence") or not sentence_data.get("phoneme"):
                return APIResponse.error(
                    message=f"Sentence {i+1}: Both sentence and phoneme are required",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate sentence length
            word_count = len(sentence_data["sentence"].split())
            if word_count < 10:
                return APIResponse.error(
                    message=f"Sentence {i+1}: Must contain at least 10 words (current: {word_count})",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            sentences_data.append({
                "id_sentence": sentence_data.get("id_sentence", i+1),
                "sentence": sentence_data["sentence"],
                "phoneme": sentence_data["phoneme"]
            })
        
        # Update the exam
        result = controller.update_exam_detail(exam_numeric_id, sentences_data)
        
        response_data = {
            "examId": test_id,
            "phonemeCategory": phoneme_category,
            "totalSentencesUpdated": len(sentences_data),
            "updatedAt": TimestampHelper.get_current_timestamp(),
            "isComplete": len(sentences_data) == 10
        }
        
        return APIResponse.success(
            data=response_data,
            message=f"Exam berhasil diperbarui dengan {len(sentences_data)} sentences"
        )
        
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            return APIResponse.error(
                message="Exam tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        return APIResponse.error(
            message=str(e.detail),
            status_code=e.status_code
        )
    except Exception as e:
        return APIResponse.error(
            message=f"Terjadi kesalahan server: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ================================
# ADDITIONAL HELPER ENDPOINTS
# ================================

@examphonemematerialrouter.get("/exam-phoneme/{phoneme_category}/validation")
def validate_exam_category(
    phoneme_category: str,
    db: Session = Depends(get_db)
):
    """Validate phoneme category for exam creation - NEW HELPER ENDPOINT"""
    try:
        controller = PronunciationMaterialController(db)
        
        # Use existing validation method
        controller._validate_category_phoneme(phoneme_category, "exam")
        
        # Get category info
        if "-" in phoneme_category:
            phonemes = [p.strip() for p in phoneme_category.split("-") if p.strip()]
            category_info = {
                "category": phoneme_category,
                "type": "similar_phonemes",
                "phonemes": phonemes,
                "phonemeCount": len(phonemes),
                "isValid": True
            }
        else:
            category_info = {
                "category": phoneme_category,
                "type": "single_phoneme",
                "phonemes": [phoneme_category],
                "phonemeCount": 1,
                "isValid": False,
                "error": "Exam materials must use similar phonemes categories"
            }
        
        return APIResponse.success(
            data=category_info,
            message="Category validation completed"
        )
        
    except HTTPException as e:
        return APIResponse.error(
            message=str(e.detail),
            status_code=e.status_code
        )
    except Exception as e:
        return APIResponse.error(
            message="Validation error occurred",
            status_code=status.HTTP_400_BAD_REQUEST
        )

@examphonemematerialrouter.get("/exam-phoneme/categories/suggest")
def suggest_exam_categories(
    db: Session = Depends(get_db)
):
    """Get suggested exam categories based on similar phonemes - NEW HELPER ENDPOINT"""
    try:
        from config.phoneme_constants import PhonemeConstants
        
        suggested_categories = []
        
        # Vowel pairs
        vowel_pairs = [
            "i-ɪ", "ɪ-ɛ", "ɛ-æ", "ə-ʌ-ɚ", "ɔ-oʊ", "oʊ-ʊ", "ʊ-u"
        ]
        
        # Consonant pairs
        consonant_pairs = [
            "p-b", "t-d", "k-g", "f-v", "θ-ð", "s-z", "ʃ-ʒ", "tʃ-dʒ", "m-n-ŋ", "l-r"
        ]
        
        # Diphthong pairs
        diphthong_pairs = [
            "eɪ-ɛ", "eɪ-ɪ", "aɪ-ɪ", "ɔɪ-ɔ", "ɔɪ-ɪ", "aʊ-ʊ"
        ]
        
        for category in vowel_pairs:
            phonemes = category.split("-")
            suggested_categories.append({
                "category": category,
                "type": "vowel_pair",
                "phonemes": phonemes,
                "description": f"Vowel contrast: {' vs '.join(phonemes)}",
                "difficulty": "medium"
            })
        
        for category in consonant_pairs:
            phonemes = category.split("-")
            suggested_categories.append({
                "category": category,
                "type": "consonant_pair", 
                "phonemes": phonemes,
                "description": f"Consonant contrast: {' vs '.join(phonemes)}",
                "difficulty": "medium"
            })
        
        for category in diphthong_pairs:
            phonemes = category.split("-")
            suggested_categories.append({
                "category": category,
                "type": "diphthong_pair",
                "phonemes": phonemes,
                "description": f"Diphthong contrast: {' vs '.join(phonemes)}",
                "difficulty": "hard"
            })
        
        return APIResponse.success(
            data={
                "suggestedCategories": suggested_categories,
                "totalSuggestions": len(suggested_categories)
            },
            message="Suggested exam categories retrieved"
        )
        
    except Exception as e:
        return APIResponse.error(
            message="Failed to get suggestions",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )